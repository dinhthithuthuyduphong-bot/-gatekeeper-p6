# Kết quả 2 — NetworkX: ô có lợi cho skill thứ hai

Ngày: **24/10/2026**. Trạng thái: **ĐÃ TÁI LẬP LOCAL — RETROSPECTIVE**.
API model: **0 lượt gọi, 0 USD**. B9: **HOLD**.

**Cập nhật CI:** run [40084717332](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40084717332) đã tái lập thành công. Raw evidence và audit ở `results/ci-40084717332/`. Các thời gian trong báo cáo gốc dưới đây là số đo local ban đầu, không đổi thành số CI. Benchmark dừng thật bổ sung ở `../research_closure/results/cost/networkx/`.

## Kết luận được bằng chứng hỗ trợ

Frozen skill `none-identity` sửa được một lỗi hành vi của NetworkX khi truyền
vị trí nút dưới dạng NumPy array. Một test do upstream viết chuyển từ lỗi
`ValueError` sang pass; cả **54 test baseline đã chọn vẫn pass**. Kết quả ổn
định trong ba lần chạy, và mã sau skill khớp AST với bản sửa upstream.

Trong generator chẩn đoán `given_positions`, Gatekeeper đạt ngưỡng admission
sau **80 draw**; 300 draw đầy đủ cho **300 help, 0 tie, 0 hurt**. Đây là một
ô có lợi đã chạy thực tế cho skill thứ hai, với nhãn **ADMIT_DIAGNOSTIC**.

## Ba nguồn được phân biệt rõ

| Vai trò | Nguồn cố định |
|---|---|
| Code trước fix | [585bb3ee251ab681e7725c07e4e8a569a0e511d5](https://github.com/networkx/networkx/tree/585bb3ee251ab681e7725c07e4e8a569a0e511d5) |
| Gold fix của upstream, 23/07/2015 | [2ae63c50fe8eb6647db18ee352bed08b21f21d91](https://github.com/networkx/networkx/commit/2ae63c50fe8eb6647db18ee352bed08b21f21d91) |
| Test hành vi từ release NetworkX 1.11 | [test_layout.py tại 0b6f608d46601fb180a0f42eaa8a9a2ca9a42ecf](https://github.com/networkx/networkx/blob/0b6f608d46601fb180a0f42eaa8a9a2ca9a42ecf/networkx/drawing/tests/test_layout.py) |

**Test witness không nằm trong commit fix năm 2015**. Đây là test
`TestLayout.test_spring_args` của bản phát hành sau, được giữ nguyên và chạy
trên snapshot trước fix. Không mô tả sai thành “test regression đi cùng PR fix”.

Môi trường: Python **3.8.20**, NumPy **1.17.5**, SciPy **1.4.1**, nose **1.3.7**,
decorator **4.4.2**, six **1.17.0**, setuptools **68.2.2**. Giấy phép NetworkX:
BSD-3-Clause, giữ cùng các file upstream trong `vendor/`.

Đây là code lịch sử được thử trong môi trường dependency khai báo ở trên.
Không khẳng định code này từng ném cùng lỗi với các dependency gốc năm 2015.
Nội dung fix upstream cũng đề cập cảnh báo về thay đổi semantics của phép so
sánh với None; do đó nên diễn giải là **sửa tương thích có lợi** trong môi trường
được đánh giá, không phóng đại thành một bug mới phát hiện ở NetworkX hiện tại.

## Bản sửa thực sự được sinh như thế nào

Nguồn skill vẫn là `study_g/skills/none-identity.json` và replay hera_pspec đã
đóng băng. Binder gốc tìm ba site trong `networkx/drawing/layout.py`:

* `_fruchterman_reingold`: `pos == None` → `pos is None`.
* `_sparse_fruchterman_reingold`: `pos == None` → `pos is None`.
* `_sparse_fruchterman_reingold`: `fixed == None` → `fixed is None`.

Không sửa tay hàm, thêm guard đặc biệt hoặc dùng gold patch để tạo treatment.
Gold chỉ dùng làm đối chứng offline: sau khi skill tự sinh patch, toàn bộ AST
của module phải khớp gold. Giữ nguyên mã test; so hash trước/sau.

## Kết quả ba lần chạy

| Nhánh / nhóm test | Pass | Functional failure | Regression trong census | Số lần lặp |
|---|---:|---:|---:|---:|
| Baseline / 2 module gốc | 54 | 0 | — | 3 |
| Baseline / upstream witness | 0 | 1 | — | 3 |
| Skill / 2 module gốc | 54 | 0 | 0 | 3 |
| Skill / upstream witness | 1 | 0 | — | 3 |
| Gold / 2 module gốc | 54 | 0 | 0 | 3 |
| Gold / upstream witness | 1 | 0 | — | 3 |

Hai module census là `networkx/drawing/tests/test_layout.py` và
`networkx/classes/tests/test_graph.py`. Đây không phải toàn bộ test suite.

Nose ghi exception của witness vào XML dưới nhãn `error`; traceback cho thấy
`ValueError: The truth value of an array ... is ambiguous` phát sinh trong thân
hàm mục tiêu tại `if pos == None`. Đây là lỗi chức năng được xác minh, không
phải import/collection/setup error. Log được giữ nguyên, không đổi nhãn XML
để tạo con số đẹp. Các lỗi môi trường khác làm kiểm định dừng thất bại.

## Ô có lợi và đối chứng

| Scope | Help / tie / hurt trên 300 draw | Điểm dừng | Kết quả họ 4 cell |
|---|---|---:|---|
| given_positions | 300 / 0 / 0 | 80 | ADMIT_DIAGNOSTIC |
| default_positions | 0 / 300 / 0 | 300 | QUARANTINE |

Generator do nghiên cứu viên viết tạo graph 3–12 nút, chọn solver dense/sparse,
có/không explicit positions, kiểm tra output hữu hạn và vị trí của nút fixed.
Nó **không** chứng minh chất lượng hoặc tính tối ưu của layout. Bằng chứng
upstream witness độc lập về nguồn được lưu riêng với generator này.

Giữ `theta=0.2`, `eta=0.05`, `alpha=0.1`, K=4. e-value nhỏ hơn trong hai chứng
chỉ tại điểm dừng là **40,5469355**, vượt ngưỡng 40. Các cell bị census phủ
quyết của SQLAlchemy vẫn nằm trong e-Holm; không bỏ cell để nâng power.

Đổi thứ tự 100 draw/scope, worker mới mỗi 25 draw: **0/200 sai khác, 0 lỗi
harness**. Sau đó môi trường mới chỉ cài đúng sáu package trong requirements
cũng tái lập cùng 18 lượt test, cùng 600 cặp outcome và không sai khác ở 200
kiểm tra trạng thái. Lần chạy thêm này không được tính thành target/skill mới.

## Chi phí và bằng chứng thô

Wall-clock trung bình census baseline **2,531 giây**, census skill **1,818 giây**;
witness baseline **1,657 giây**, witness skill **1,335 giây**. Đến admission của
generator mất **1,8334 giây**, chạy đủ 300 draw mất **2,5061 giây** trong lần đo
chính. Máy chạy, import và lịch cấp CPU ảnh hưởng đáng kể; không suy ra speedup
đáng tin cậy từ những thời gian ngắn này. Toàn bộ đo đạc/replay không gọi model.

Xem `results/2026-10-24/networkx/`: `RESULT.md`, `RESULT.json`, manifest, patch,
18 cặp log/XML, `draws.jsonl`, log đổi thứ tự và `STATELESSNESS.json`.
Môi trường sạch: `results/2026-10-24/clean_networkx_replay/` và
`clean_replay_check.json`. Đường dẫn trong báo cáo tính từ `study_i/` của gói ZIP.

## Giới hạn bắt buộc giữ khi viết paper

Target và scope được tìm sau khi xem dữ liệu, nên đây là **hồi cứu/khám phá**.
Nguồn upstream giúp tránh tự đặt kỳ vọng tùy ý, nhưng không biến selection này
thành đánh giá tiến cứu. Generator `given_positions` cố ý tập trung vào vùng
được sửa; 300/300 help không phải tỷ lệ cải thiện trên mọi lệnh gọi NetworkX.

Kết quả tháo gỡ tình trạng “chưa có beneficial behavioral case” của skill 2 ở
mức artifact thực thi. Nó chưa chứng minh tỷ lệ chuyển giao rộng, độc lập với
model, ưu thế so với B9 hoặc an toàn trên mọi input ngoài scope.
