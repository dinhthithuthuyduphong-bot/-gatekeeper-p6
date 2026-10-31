# Kiểm trích dẫn của bản nháp (PAPER_TODO 4.4)

Ngày 31/10/2026, tra bằng tìm kiếm web. Phiên của trợ lý không vào thẳng được arxiv.org, nên mỗi mục được đối chiếu qua trang listing hoặc tóm tắt của arXiv và các trang tổng hợp.

**Kết luận:** cả 7 mục có tác giả placeholder ("… Authors") đều **là bài có thật** ở đúng mã arXiv. Nhưng **tên bài trong bản nháp sai hoặc bịa** ở cả 7 mục, và không mục nào có tác giả thật. Bản bài mới (`latex/refs.bib`) dùng tên và tác giả đã tra. Mục nào chỉ biết tác giả đầu thì ghi "and others" và **phải bổ sung đủ tác giả từ PDF trước khi nộp**.

| Mục trong bản nháp | Tên trong bản nháp | Tên thật | Tác giả (đã tra) | Ngày | Dùng trong bài mới? |
|---|---|---|---|---|---|
| [6] GSE, arXiv:2608.06153 | "GSE: Globally Reusable Skill Evolution for Coding Agents" | **Learning Globally Reusable Skills for Coding Agents** | Chen Yang, Jiashuo Tian, Ziqi Wang, Xinyin Liu, Meiru Ye, Junjie Chen | 8/2026 | Có, đây là baseline gần nhất |
| [5] arXiv:2605.23951 | "Formal Verification of Learned Agent Skills and Capability Containment" | **Methods for Formal Verification of Agent Skills: Three Layers Toward a Mechanically Checkable Capability-Containment Proof** | Alfredo Metere | 9/5/2026 | Có |
| [8] MemCoder, arXiv:2603.13258 | "MemCoder: Structured Intent-to-Code Experience Memory for Coding Agents" | **Your Code Agent Can Grow Alongside You with Structured Memory** | Yi-Xuan Deng và 4 đồng tác giả (cần bổ sung) | 2/2026 | Có |
| [9] MemGovern, arXiv:2601.06789 | "MemGovern: Governed Development Histories as Reusable Experience Cards" | **MemGovern: Enhancing Code Agents through Learning from Governed Human Experiences** | Qihao Wang, Ziming Cheng, … (cần bổ sung) | 11/1/2026 | Có |
| [11] TMA-NM | "TMA-NM: Trust Management and Authority for Agent Memory", không có mã arXiv | **Securing LLM-Agent Long-Term Memory Against Poisoning: Non-Malleable, Origin-Bound Authority with Machine-Checked Guarantees** (arXiv:2606.24322) | chưa tra được | 6/2026 | Không (chưa đủ thông tin) |
| Reading [6] CooperBench, arXiv:2601.13295 | "CooperBench: Measuring collaborative conflicts between coding agents" | **CooperBench: Why Coding Agents Cannot be Your Teammates Yet** | Stanford và SAP Labs (cần bổ sung) | 19/1/2026 | Không |
| Reading [8] GEM/MemState, arXiv:2605.26252 | "GEM/MemState: Dependency-aware correctness for agent memory" | **Is Agent Memory a Database? Rethinking Data Foundations for Long-Term AI Agent Memory** | Abdelghny Orogat, Essam Mansour | 25/5/2026 | Không |
| Reading [15] ReasoningBank | không có mã | *ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory* (arXiv:2509.25140): theo hiểu biết của trợ lý, **chưa tra trong phiên** | — | 2025 | Không |

Các mục kinh điển của bản nháp (LTT, CRC, BH, CaMeL, Howard et al., Progent, Vovk et al., Voyager, Waudby-Smith & Ramdas, SWE-bench) có thông tin xuất bản khớp với hiểu biết hiện có và vẫn dùng.

**Nguồn tra (trang tìm kiếm):** listing arXiv của 2608.06153, 2605.23951, 2603.13258, 2601.06789, 2606.24322, 2601.13295, 2605.26252, cùng các trang alphaxiv, emergentmind, huggingface papers tương ứng.

**Việc còn lại trước khi nộp:** mở PDF của MemCoder, MemGovern (và CooperBench, TMA-NM nếu dùng) để chép đủ danh sách tác giả.
