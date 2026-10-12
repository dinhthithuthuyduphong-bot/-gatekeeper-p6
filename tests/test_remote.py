import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json
import subprocess

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',root/'RUN_P6_REMOTE.py')
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
IMAGE='sha256:'+'a'*64
RID='b'*32

class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name).resolve()
        self.obj={'Image':IMAGE,'HostConfig':{'NetworkMode':'none','ReadonlyRootfs':True,'Privileged':False,'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges:true'],'NanoCpus':1000000000,'Memory':268435456,'MemorySwap':268435456,'PidsLimit':64},'Config':{'User':'65534:65534','Labels':{r.LABEL:RID},'Env':['PYTHONHASHSEED=1729']},'Mounts':[{'Type':'bind','Source':str(self.folder),'Destination':'/work','RW':False}]}
    def test_reject_mutable_image(self):
        with self.assertRaises(ValueError):r.image_id('python:latest')
    def test_reject_injection(self):
        with self.assertRaises(ValueError):r.image_id(IMAGE+'; echo bad')
    def test_command_limits(self):
        cmd=r.create_command(IMAGE,self.folder,RID)
        for flag in ('--pull=never','--network=none','--read-only','--cap-drop=ALL','--pids-limit=64','--memory=256m'):
            self.assertIn(flag,cmd)
        self.assertNotIn('--privileged',cmd)
        self.assertNotIn('/var/run/docker.sock',' '.join(cmd))
    def test_configuration_valid(self):
        self.assertTrue(all(r.verify_settings(self.obj,IMAGE,self.folder,RID).values()))
    def test_reject_network(self):
        self.obj['HostConfig']['NetworkMode']='host'
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_reject_root(self):
        self.obj['Config']['User']='0'
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_reject_writable_mount(self):
        self.obj['Mounts'][0]['RW']=True
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_reject_extra_host_mount(self):
        self.obj['Mounts'].append({'Type':'bind','Source':'/tmp','Destination':'/other','RW':True})
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_reject_token(self):
        self.obj['Config']['Env'].append('GITHUB_TOKEN=DO_NOT_USE')
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_reject_wrong_owner(self):
        self.obj['Config']['Labels'][r.LABEL]='c'*32
        with self.assertRaises(ValueError):r.verify_settings(self.obj,IMAGE,self.folder,RID)
    def test_synthetic_control(self):
        before,after={},{}
        exec(r.BASELINE,before)
        exec(r.TREATMENT,after)
        self.assertEqual(before['classify'](True),'integer')
        self.assertEqual(after['classify'](True),'other')
        for value in (0,1,'1',None,1.5):
            self.assertEqual(before['classify'](value),after['classify'](value))
    def test_timeout_cleans_only_owned_container(self):
        cid='c'*64
        calls=[]
        def fake(command,timeout=20):
            calls.append(command)
            if command[1]=='create':return cid
            if command[1]=='inspect':return json.dumps([{'Config':{'Labels':{r.LABEL:RID}}}])
            if command[1]=='start':raise subprocess.TimeoutExpired(command,timeout)
            if command[1]=='rm':return cid
            raise AssertionError(command)
        with patch.object(r,'checked',side_effect=fake),patch.object(r,'verify_settings',return_value={}):
            with self.assertRaises(subprocess.TimeoutExpired):r.one_arm(IMAGE,'baseline',self.folder,RID)
        self.assertEqual(calls[-1],['docker','rm','--force',cid])
    def test_does_not_remove_unowned_container(self):
        cid='c'*64
        calls=[]
        def fake(command,timeout=20):
            calls.append(command)
            if command[1]=='create':return cid
            if command[1]=='inspect':return json.dumps([{'Config':{'Labels':{r.LABEL:'d'*32}}}])
            raise AssertionError(command)
        with patch.object(r,'checked',side_effect=fake),patch.object(r,'verify_settings',side_effect=ValueError('ownership mismatch')):
            with self.assertRaises(ValueError):r.one_arm(IMAGE,'baseline',self.folder,RID)
        self.assertFalse(any(c[1]=='rm' for c in calls))
    def test_no_install_or_shell_runner(self):
        import ast
        code=ast.parse((root/'RUN_P6_REMOTE.py').read_text())
        for node in ast.walk(code):
            if isinstance(node,ast.Call):
                self.assertFalse(any(k.arg=='shell' and isinstance(k.value,ast.Constant) and k.value.value for k in node.keywords))

if __name__=='__main__':unittest.main()
