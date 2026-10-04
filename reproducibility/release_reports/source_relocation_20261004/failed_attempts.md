# 本轮核查的失败记录

## 第一次迁移后核查

- 命令：`python -B reproducibility/release_reports/source_relocation_20261004/verify.py verify`
- 实际退出码：1。
- 停止位置：读取冻结来源 `scripts/verify_release.py` 的子进程标准输出。
- 原因：Windows 子进程以本机代码页输出中文，父进程以 UTF-8 解码；出现 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in position 79: invalid continuation byte`，随后 `json.loads(locked.stdout)` 因结果为 `None` 报错。
- 此时冻结包迁移前后 87 个文件哈希、保护材料和源码仅路径变更的比较已执行；独立工作区和文案回归尚未执行。不将整项检查记为通过。
- 修复仅限本轮核查脚本：为子进程显式指定 `PYTHONIOENCODING=utf-8`，不改冻结脚本、正式复现计算接口或原始材料。

## 第二次迁移后核查

- 同一命令实际退出码为 1；冻结锁定文件检查已通过，停止于加载发布入口，错误为 `ModuleNotFoundError: No module named 'pymupdf'`。
- 原因：PATH 中的 `E:/anaconda/python.exe` 不是项目此前验收所用的虚拟环境；没有安装新依赖或修改入口。
- 改用现有的 `reproducibility/.venv/Scripts/python.exe` 重试。前两次均在创建独立工作区前停止，失败记录保留。
