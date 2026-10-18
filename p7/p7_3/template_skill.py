"""Strict source-derived AST templates. No target outcomes enter induction.

This is a curated-source/deterministic-template hybrid, not an LLM skill learner.
Matching a whole function is deliberately narrow; transfer remains unvalidated.
"""
import ast
import copy
import hashlib

def find_scope(tree, path):
    nodes=[tree]
    for name in path.split('.'):
        nodes=[n for parent in nodes for n in getattr(parent,'body',[])
               if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    if len(nodes)!=1 or not isinstance(nodes[0],(ast.FunctionDef,ast.AsyncFunctionDef)):
        raise ValueError('Scope must identify exactly one function')
    return nodes[0]

def local_names(node):
    names=[]
    for n in ast.walk(node):
        value=n.arg if isinstance(n,ast.arg) else n.id if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store) else None
        if value and value not in names: names.append(value)
    return names

class Rename(ast.NodeTransformer):
    def __init__(self,mapping): self.mapping=mapping
    def visit_Name(self,node):
        node.id=self.mapping.get(node.id,node.id); return node
    def visit_arg(self,node):
        node.arg=self.mapping.get(node.arg,node.arg); return self.generic_visit(node)

class NoDocstrings(ast.NodeTransformer):
    def generic_visit(self,node):
        node=super().generic_visit(node)
        if isinstance(node,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
                node.body=node.body[1:]
        return node

def semantic_dump(tree):
    return ast.dump(NoDocstrings().visit(copy.deepcopy(tree)),include_attributes=False)

def canonical(node):
    node=copy.deepcopy(node)
    names=local_names(node)
    node=Rename({name:f'__gk_local_{i}' for i,name in enumerate(names)}).visit(node)
    return semantic_dump(node)

def learn(before,after,scope):
    b,a=ast.parse(before),ast.parse(after)
    bf,af=find_scope(b,scope),find_scope(a,scope)
    old_imports={ast.dump(n,include_attributes=False) for n in b.body if isinstance(n,(ast.Import,ast.ImportFrom))}
    new_imports=[]
    previous=None
    for n in a.body:
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            rendered=ast.unparse(n)
            if ast.dump(n,include_attributes=False) not in old_imports:
                new_imports.append({'source':rendered,'after':previous})
            previous=rendered
    if canonical(bf)==canonical(af): raise ValueError('No behavioral AST change')
    result={'schema':'gk_strict_function_template_v1','scope':scope,
            'before_pattern':canonical(bf),'before_locals':local_names(bf),
            'after_function':ast.unparse(af),'added_imports':new_imports,
            'induction':'curated-source + deterministic AST template; no transfer claim'}
    generated=apply(before,result)
    if semantic_dump(ast.parse(generated))!=semantic_dump(a):
        raise ValueError('Changes extend beyond supported function/import template')
    return result

def apply(source,skill):
    if skill['schema']!='gk_strict_function_template_v1': raise ValueError('Unsupported schema')
    tree=ast.parse(source); target=find_scope(tree,skill['scope'])
    if canonical(target)!=skill['before_pattern']: raise ValueError('Precondition mismatch; do not apply')
    names=local_names(target)
    if len(names)!=len(skill['before_locals']): raise ValueError('Binding mismatch')
    replacement=ast.parse(skill['after_function']).body[0]
    replacement=Rename(dict(zip(skill['before_locals'],names))).visit(replacement)
    replacement.name=target.name
    start=min([target.lineno]+[d.lineno for d in target.decorator_list])-1
    lines=source.splitlines(keepends=True)
    indent=' '*target.col_offset
    rendered='\n'.join(indent+line if line else line for line in ast.unparse(ast.fix_missing_locations(replacement)).splitlines())+'\n'
    lines[start:target.end_lineno]=[rendered]
    output=''.join(lines)
    for addition in skill['added_imports']:
        tree=ast.parse(output)
        imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        existing={ast.unparse(n):n for n in imports}
        if addition['source'] in existing: continue
        if addition['after'] not in existing: raise ValueError('Import anchor mismatch')
        position=existing[addition['after']].end_lineno
        lines=output.splitlines(keepends=True)
        lines[position:position]=[addition['source']+'\n']
        output=''.join(lines)
    ast.parse(output)
    return output
