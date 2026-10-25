# Gatekeeper-Lite — kết quả đợt xử lý điểm yếu, 24/10/2026

**Đã sửa phần chấm điểm, bổ sung đối chứng thống kê công bằng hơn, đo chi phí dừng thật và kiểm toán bằng chứng. Chưa giải quyết xong khả năng khái quát hay hiệu quả theo model.** Không gọi model, không phát sinh phí API; B9 vẫn `HOLD`.

Gói được xây trên `main` tại `fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293` và kiểm tra local. Người dùng cần đưa gói lên `main` rồi chạy workflow mới. Các phân tích bổ sung dưới đây là **hậu kiểm/thăm dò**, không được đổi nhãn thành nghiên cứu tiến cứu.

## 1. Đã hoàn tất những gì

| Vấn đề | Thay đổi và bằng chứng | Trạng thái thực chất |
|---|---|---|
| Study F có thể lỗi khi in candidate hoặc tổng hợp thiếu dữ liệu | Sửa `tools/score_heldout.py`, `tools/aggregate_study_f.py`; thêm `gatekeeper_ext/study_f_validation.py` | Đã sửa và kiểm thử local; chưa có model outcomes mới |
| Bằng chứng B9 chưa kiểm tra đủ | Yêu cầu đủ 72 raw patches + 72 candidate rows; đủ scope và 300 observations; kiểm tra trace/count/verdict, usage, replay, seed, config/source hashes; tính lại e-value từ trace | Thiếu/mâu thuẫn dữ liệu làm dừng chấm điểm, không tự điền zero |
| Fixed-skill comparator chưa đồng nhất cổng an toàn mọi scope | Áp cùng quy tắc mức patch, trong họ riêng sáu fixed patches; dữ liệu cũ vẫn chỉ D1 và D3 được chọn | F-A3 có khai báo; không thay kết quả chính Study D |
| So sánh fixed-size có thể chịu thiệt do chia alpha thừa | Thêm intersection–union test `max(p_benefit,p_harm)` và Holm/Bonferroni, chạy lại cùng 50 họ Study H | Có baseline mạnh hơn; không còn đủ căn cứ tuyên bố GK thắng chung |
| Harm certificate yếu gần ngưỡng | Đo adaptive và balanced-mixture, tính power chính xác của cổng harm fixed-n | Không có cải thiện đồng đều; primary giữ nguyên |
| Chi phí chỉ dựa trên replay số draws | Chạy sequential thực và full-draw thực, cùng selected-module census và setup, ba lần mỗi chính sách/target | Có số wall-clock đo thật trên hai target đã biết |
| Khó tái lập/nhầm log cũ với log CI mới | Workflow Study I ghi evidence vào thư mục tạm riêng của runner; thêm workflow audit 0 API | Workflow mới đã kiểm tra local; chưa chạy remote trong đợt này |
| Thiếu cohort độc lập | Tạo Study J protocol/preflight, danh sách loại repo đã khảo sát; ghim và quét tĩnh thêm 12 repo | Chưa có cohort đủ điều kiện, Study J vẫn `BLOCKED` |

F-A3 lưu config/freeze F-A2 trong `study_f/amendment_archive/F-A2/`. Seed gốc giữ nguyên: `c1e57be377bb282baba53d4b646138f97ec1843effb634d89f9bc59d8b6ed021`. Không đổi model, giá, quota, target/oracle, theta, eta, alpha hoặc n_max; cũng không xác nhận các model ID/giá lịch sử còn hiện hành. Metadata cassette là kiểm tra nhất quán, không phải xác thực mật mã của nhà cung cấp.

## 2. Kết quả thống kê — có cả kết quả bất lợi

Trên cùng 50 họ dữ liệu Study H, mỗi họ gồm sáu ô với mức hại 0%, 1%, 2%, 3%, 5%, 10%:

| Chính sách | Admit tại h=2% | Admit tại h=3% | Draw/họ trung bình | Họ có admit sai |
|---|---:|---:|---:|---:|
| GK gốc | 17/50 | 11/50 | 1.300,50 | 0/50 |
| GK adaptive, hậu kiểm | 14/50 | 8/50 | 1.342,34 | 0/50 |
| GK balanced mixture, hậu kiểm | 21/50 | 11/50 | 1.362,54 | 0/50 |
| Fixed 200, IUT Holm | 19/50 | 15/50 | 1.200 | 0/50 |
| Fixed 300, IUT Holm | 35/50 | 16/50 | 1.800 | 0/50 |

**Không thay primary bằng adaptive:** lần thử này kém hơn. Mixture cải thiện một ô nhưng tốn thêm draws và không thắng đồng đều. Fixed-200 tốt hơn GK ở hai mức hại trên với ít draws hơn; ở h=1%, GK vẫn tốt hơn (45/50 so với 42/50). Đây là đánh đổi, không phải dominance.

0/50 họ có lỗi không chứng minh FWER bằng 0; cận trên nhị thức một phía 95% là **5,8155%**. Bảng này là replay trên trace, không phải đo wall-clock. Baseline lợi ích dùng Hoeffding nên chưa phải fixed-size mạnh nhất có thể.

Với eta=5%, alpha/K=0,1/6 và hại thật 3%, xác suất vượt **riêng cổng harm** ở n=300 chỉ khoảng 32%; n=1.000 khoảng 84,6%. Đây không phải power của toàn bộ admission, vì còn cổng lợi ích/census. Khó khăn gần biên an toàn không thể loại bỏ chỉ bằng đổi stake.

Bảng đầy đủ và log: [STATISTICS_RESULT.md](results/statistics/STATISTICS_RESULT.md), `families.jsonl`, `POWER_PLANNING.json`.

## 3. Chi phí đo thật

Mỗi target chạy ba lần cho mỗi chính sách, đổi thứ tự chính sách theo lịch đã ghi trước. Hai target cuối cùng chạy nối tiếp trên máy, tránh tranh tài nguyên. Mỗi nhánh trả chi phí snapshot, selected-module census, worker và ghi journal; không tính download/cài dependency.

| Target | Sequential, giây TB | Full draws, giây TB | Giảm tổng thời gian | Paired draws/lần, sequential → full |
|---|---:|---:|---:|---:|
| SQLAlchemy | 40,7262 | 47,6469 | **14,53%** | 303 → 600 |
| NetworkX | 5,8268 | 6,4333 | **9,43%** | 380 → 600 |

Đã kiểm toán **12 measurement arms, 24 XML census và 5.649 paired draws**: journal khớp trace/counts, census khớp regression list, hai chính sách khớp prefix/decision/evidence tại điểm dừng, trung bình tính lại đúng. Số đo cụ thể thuộc máy và workload này; ba lần đo không phải ba repo độc lập và không đủ để hứa speedup tổng quát.

**SQLAlchemy đã bị census bắt hại.** So sánh trên cho thấy tiết kiệm so với *census + chạy đủ draws*, không chứng minh rẻ hơn census-only. Tất cả vẫn là trial không gọi model, nên chưa trả lời hiệu quả trong vòng lặp LLM đắt tiền.

Báo cáo: [SQLAlchemy](results/cost/sqlalchemy/COST_RESULT.md), [NetworkX](results/cost/networkx/COST_RESULT.md). Raw log, XML, draw input/output và số đo từng lần nằm cạnh báo cáo. Các lần đo ban đầu chạy chồng nhau được giữ trong `results/cost/concurrent_attempt/` nhưng không dùng cho bảng cuối; lý do là cách ly tài nguyên, không phải chọn kết quả có lợi.

## 4. Skill thứ hai và giới hạn của target mới

Bằng chứng đã có trên `main` vẫn đứng vững: SQLAlchemy thêm target có hại với test upstream không đổi; NetworkX thêm trường hợp sửa có lợi với test upstream ở phiên bản sau làm behavioral witness. Witness NetworkX không phải test của đúng commit fix, nên phải giữ mô tả nguồn như trong Study I. Đây là hai case hồi cứu, không tự khép được khoảng trống generalization.

Đợt này ghim và quét tĩnh 12 repo khác: anyio, APScheduler, schedule, Arrow, Pendulum, HTTPX, Starlette, structlog, referencing, marshmallow, itsdangerous, pydantic-settings. Kết quả:

- 37 vị trí khớp skill bool/int trong bảy repo; 13 vị trí có tham chiếu tên hàm và literal bool trong test để điều tra tiếp.
- **0 vị trí khớp skill none-identity** tại 12 commit đã ghim; chưa tìm thêm target cho skill thứ hai từ đợt quét này.
- Không chạy test/treatment ở các repo mới; tên hàm/literal trùng không phải oracle đã xác minh. Không gán tier-1, lợi/hại hoặc eligible chỉ từ quét AST.

Xem [SCREEN_RESULT.md](results/candidate_screen/SCREEN_RESULT.md) và JSON/log từng repo. Study J chỉ có thiết kế, exposure ledger và hồ sơ ứng viên; chưa có target đủ điều kiện trong config, public freeze hay post-freeze outcome. Preflight trả `BLOCKED` là đúng.

## 5. Model và kỳ vọng của paper

Skill AST đã đóng băng có thể chạy không cần model. Điều đó chưa chứng minh hiệu quả không phụ thuộc model: model khác tạo phân phối patch khác. Study F đã chuẩn bị báo cáo riêng theo model/target, gồm harmful patches bị chặn, successful patches được giữ/bị loại và chi phí.

Vì raw và gated dùng cùng patch, `SUCCESS_gated <= SUCCESS_raw` theo thiết kế. Gatekeeper là bộ lọc triển khai, không phải bước cải thiện patch. Model không tạo harmful raw patch thì khả năng chặn hại trên model đó **chưa được đánh giá**, không được báo 100%.

Đối chiếu ba tài liệu FSE-2027-13 cho thấy headline là dự phóng; không đưa chúng vào bảng kết quả repo. Audit cũng nêu hai điểm cần làm rõ về hệ số total variation và cận composition trước khi kế thừa mệnh đề. Chi tiết: [PAPER_EXPECTATION_AUDIT.md](PAPER_EXPECTATION_AUDIT.md). Không đưa PDF riêng của người dùng vào gói public.

## 6. Kiểm chứng và việc còn mở

`results/final_validation_v2/VALIDATION.json`: **PASS_ZERO_PAID_API_CHECKS**. Toàn bộ **125 unit tests** qua; freeze D/E/F/G/H hợp lệ; `results_check` qua; Study I CI được tính lại từ raw; thống kê và chi phí được kiểm toán lại; paid preflight dù giả lập ngày sau 31/10 vẫn chặn bằng `HOLD`. Kiểm tra workflow có trigger, quyền đọc và dưới giới hạn 500 KB. Đây là kiểm tra local, không phải run GitHub mới.

Log lỗi ban đầu được giữ: hai fixture test cũ chưa đáp ứng schema mới; scanner ban đầu quên đăng ký extension; hai lần khởi tạo benchmark lỗi và lần đo tranh tài nguyên. Không lấy các lần này làm bằng chứng hiệu quả.

Những việc **chưa được giải quyết bằng kết quả mới**:

1. Cohort repo độc lập cho cả hai skill, oracle đủ mạnh, baseline ổn định, public freeze trước treatment. Đặc biệt skill thứ hai vẫn thiếu độ rộng.
2. Ưu thế trước replay + dependency fingerprint + smoke/census mạnh ở mức giữ lại beneficial patches tương đương. Kết quả fixed-size mới cho thấy cần chấp nhận cả khả năng GK không thắng.
3. Hiệu quả theo model và lợi ích kinh tế khi có LLM. Harness sẵn sàng kiểm tra bằng chứng hơn, nhưng chưa có paid/free-provider outcomes mới.
4. Bằng chứng composition/retirement ngoài demo và phạm vi hai skill. Chưa được mở rộng trong đợt này.

Không gọi repo “100% hoàn tất nghiên cứu”. Phần triển khai/kiểm toán đã tiến thêm; một số câu hỏi khoa học vẫn cần thí nghiệm mới và có thể cho kết quả âm. Cách đưa gói lên main và chạy kiểm tra: [UPDATE_MAIN.md](UPDATE_MAIN.md).
