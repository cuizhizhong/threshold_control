# NEW-4a 复现收尾（2026-10-19）

基准8157fcd，工作树E:/work/draft-submission-ready。两项均需修改：4个图7输入在CRLF工作树记录raw SHA，在LF检出会误拒绝缓存；收敛JSON原来被终点审计和宏生成器裸读，第二输入的身份及实际数字读取链缺登记。

## 本轮修补

- 对点名代码、weight_brackets和图7/终点派生JSON精确设text eol=lf，写出端显式UTF-8/LF。未全仓库renormalize。原phase.json、NPZ和冻结来源继续原始字节校验。
- 图7source_hashes迁为对应LF文件的raw SHA。旧source_hashes全集、原记录SHA、历史compute_script及background脚本身份保存在identity_history和new4a_identity_migration.json。cases、背景数组与本地NPZ不改；纯缓存路径禁止进入分类、控制律求值或背景细化。
- 第二输入r7_3_convergence.json精确-text，恢复固定Git原始LF字节；bb52b965与归档9887340相同。SHA256=bbd7e4ea49a1d8e94623c3c2d27bdc67d690b592a5c189a01129a17f150b1d3b，blob=5dde27d9bb447ef7896f63642dfd33f54cbb8f0f。
- IR共用原始字节校验器，读取收敛文件前强制SHA/blob及54条记录完整性校验；ep登记convergence_source。宏生成前再次验证该来源与ep字段，然后只从ep的solver_tolerance_max_rel_tight读取容差，不再裸读源文件取值。容差仍为2.5072481505952823e-11。
- 原simplified attributes测试已换成仓库真实.gitattributes全文和真实相对路径，在autocrlf=true/false检出后逐字节比较，且实查text/eol。不是Linux系统实测。

## 实际验收

48项受影响测试通过，0失败/跳过。首次测试时旧render收据尚未刷新为LF，真实路径测试捕获此状态；完成缓存重绘及所有派生JSON写出修补后通过。没有改数值真值或容差。

真实运行plot_figure7.py --reuse-data；另在无.git新目录删除中间结果后执行终点审计、108宏生成和缓存重绘成功。第二输入追加换行后，终点CLI和宏CLI均以SHA错误失败，原宏不被覆盖；随后恢复副本。完整日志/摘要见new4a_reproducibility.json。

18行终点、6组尾界、108宏与NEW-4完全相同；宏文件逐字节相同。主35页、补19页构建通过，最终日志无未定义引用/文献、重复标签、缺字、Overfull或重跑提示。全部54页按72 dpi比较与NEW-4逐页像素相同，数学与数值、图7格式均不变。图7碰撞0失败/0警告，PDF字形最小5.6 pt，布局gate通过。

未重跑权重分类、背景计算或回流ODE。没有计划外实质数学修改。用户随后NEW-4b第6项要求改为文本内容规范化哈希，将在独立下一提交落实；本提交保留本轮精确LF/raw身份修补的历史。
