# 快捷键总表

## 说明
- 这份配置当前没有启用额外自定义键位文件：`lua/plugins/astrocore.lua`、`lua/polish.lua`、`lua/plugins/user.lua`、`lua/community.lua` 都被直接禁用。
- 因此，下面整理的是当前实际生效的完整键位：AstroNvim 默认键位、随配置加载的插件默认键位，以及运行时保留下来的 Neovim 默认映射。
- `<Leader>` 实际是空格键，`<LocalLeader>` 实际是 `,`。本配置没有检测到额外的 `<LocalLeader>` 映射。
- 本次按运行时实际导出到 `:map` 的结果整理，共 `269` 条：普通模式 `219`、可视模式 `24`、选择模式 `4`、操作等待模式 `9`、插入模式 `7`、终端模式 `6`。命令行模式和 Lang-Arg 模式没有检测到生效映射。
- `插件内部 <Plug> 映射` 也单独列出，目的是做到不遗漏；这类映射通常供插件或其它快捷键间接调用，不建议手动记忆。

## 普通模式：文件、主页、保存与退出

- `<C-Q>`：强制退出（普通模式）
- `<C-S>`：强制写入文件（普通模式）
- `<Leader>Q`：退出 AstroNvim（普通模式）
- `<Leader>R`：重命名文件（普通模式）
- `<Leader>h`：返回首页（普通模式）
- `<Leader>n`：新建文件（普通模式）
- `<Leader>q`：退出当前窗口（普通模式）
- `<Leader>w`：保存文件（普通模式）

## 普通模式：会话

- `<Leader>S.`：加载当前目录会话（普通模式）
- `<Leader>SD`：删除目录会话（普通模式）
- `<Leader>SF`：加载目录会话（普通模式）
- `<Leader>SS`：保存当前目录会话（普通模式）
- `<Leader>Sd`：删除会话（普通模式）
- `<Leader>Sf`：加载会话（普通模式）
- `<Leader>Sl`：加载上一个会话（普通模式）
- `<Leader>Ss`：保存当前会话（普通模式）
- `<Leader>St`：保存当前标签页会话（普通模式）

## 普通模式：缓冲区与标签栏

- `<Leader>C`：强制关闭缓冲区（普通模式）
- `<Leader>bC`：关闭所有缓冲区（普通模式）
- `<Leader>b\`：从标签栏水平分屏打开缓冲区（普通模式）
- `<Leader>bb`：从标签栏选择缓冲区（普通模式）
- `<Leader>bc`：关闭除当前外的所有缓冲区（普通模式）
- `<Leader>bd`：从标签栏关闭缓冲区（普通模式）
- `<Leader>bl`：关闭左侧所有缓冲区（普通模式）
- `<Leader>bp`：上一个缓冲区（普通模式）
- `<Leader>br`：关闭右侧所有缓冲区（普通模式）
- `<Leader>bse`：按扩展名排序（普通模式）
- `<Leader>bsi`：按缓冲区编号排序（普通模式）
- `<Leader>bsm`：按修改时间排序（普通模式）
- `<Leader>bsp`：按完整路径排序（普通模式）
- `<Leader>bsr`：按相对路径排序（普通模式）
- `<Leader>b|`：从标签栏垂直分屏打开缓冲区（普通模式）
- `<Leader>c`：关闭缓冲区（普通模式）
- `<lt>b`：把缓冲区标签左移（普通模式）
- `>b`：把缓冲区标签右移（普通模式）
- `[B`：跳到第一个缓冲区（普通模式）
- `[b`：上一个缓冲区（普通模式）
- `]B`：跳到最后一个缓冲区（普通模式）
- `]b`：下一个缓冲区（普通模式）

## 普通模式：文件树、窗口、列表与分屏

- `<C-Down>`：向下增大分屏（普通模式）
- `<C-H>`：移动到左侧窗口（普通模式）
- `<C-K>`：移动到上方窗口（普通模式）
- `<C-L>`：移动到右侧窗口（普通模式）
- `<C-Left>`：向左增大分屏（普通模式）
- `<C-Right>`：向右增大分屏（普通模式）
- `<C-Up>`：向上增大分屏（普通模式）
- `<C-W><C-D>`：显示光标下诊断信息（普通模式）
- `<C-W>d`：显示光标下诊断信息（普通模式）
- `<Leader>e`：切换文件树（普通模式）
- `<Leader>o`：聚焦文件树（普通模式）
- `<Leader>xl`：打开 Location List（普通模式）
- `<Leader>xq`：打开 Quickfix List（普通模式）
- `<NL>`：移动到下方窗口（普通模式）
- `\`：水平分屏（普通模式）
- `|`：垂直分屏（普通模式）

## 普通模式：搜索与查找

- `<Leader>f'`：查找标记（普通模式）
- `<Leader>f<CR>`：恢复上一次搜索（普通模式）
- `<Leader>fC`：查找命令（普通模式）
- `<Leader>fF`：查找全部文件（普通模式）
- `<Leader>fO`：查找当前目录最近文件（普通模式）
- `<Leader>fT`：查找 TODO 注释（普通模式）
- `<Leader>fW`：在全部文件中查找单词（普通模式）
- `<Leader>fa`：查找 AstroNvim 配置文件（普通模式）
- `<Leader>fb`：查找缓冲区（普通模式）
- `<Leader>fc`：查找光标下单词（普通模式）
- `<Leader>ff`：查找文件（普通模式）
- `<Leader>fg`：查找 Git 跟踪文件（普通模式）
- `<Leader>fh`：查找帮助（普通模式）
- `<Leader>fk`：查找键位映射（普通模式）
- `<Leader>fl`：查找当前缓冲区行（普通模式）
- `<Leader>fm`：查找 man 手册（普通模式）
- `<Leader>fn`：查找通知记录（普通模式）
- `<Leader>fo`：查找最近文件（普通模式）
- `<Leader>fp`：查找项目（普通模式）
- `<Leader>fr`：查找寄存器（普通模式）
- `<Leader>fs`：查找缓冲区、最近文件和文件（普通模式）
- `<Leader>ft`：查找主题（普通模式）
- `<Leader>fu`：查找撤销历史（普通模式）
- `<Leader>fw`：查找单词（普通模式）

## 普通模式：Git

- `<Leader>gC`：查看当前文件提交记录（普通模式）
- `<Leader>gT`：查看 Git stash（普通模式）
- `<Leader>gb`：查看 Git 分支（普通模式）
- `<Leader>gc`：查看仓库提交记录（普通模式）
- `<Leader>gg`：打开或切换 lazygit 终端（普通模式）
- `<Leader>go`：打开当前仓库或文件的 Git 浏览页面（普通模式）
- `<Leader>gt`：查看 Git 状态（普通模式）

## 普通模式：LSP、诊断与符号

- `<Leader>lD`：搜索诊断信息（普通模式）
- `<Leader>lS`：打开符号大纲（普通模式）
- `<Leader>ld`：查看悬浮诊断（普通模式）
- `<Leader>li`：查看 LSP 信息（普通模式）
- `<Leader>ls`：搜索符号（普通模式）
- `gO`：列出当前文档符号（普通模式）
- `gl`：查看悬浮诊断（普通模式）
- `gra`：代码操作（普通模式）
- `gri`：跳转到实现（普通模式）
- `grn`：重命名符号（普通模式）
- `grr`：列出引用（普通模式）
- `grt`：跳转到类型定义（普通模式）

## 普通模式：调试

- `<F10>`：调试：单步跳过（普通模式）
- `<F11>`：调试：单步进入（普通模式）
- `<F17>`：调试：停止（普通模式）
- `<F21>`：调试：条件断点（普通模式）
- `<F23>`：调试：单步跳出（普通模式）
- `<F29>`：调试：重启（普通模式）
- `<F5>`：调试：开始（普通模式）
- `<F6>`：调试：暂停（普通模式）
- `<F9>`：调试：切换断点（普通模式）
- `<Leader>dB`：清除全部断点（普通模式）
- `<Leader>dC`：设置条件断点（普通模式）
- `<Leader>dE`：执行调试表达式（普通模式）
- `<Leader>dO`：单步跳出（普通模式）
- `<Leader>dQ`：终止调试会话（普通模式）
- `<Leader>dR`：打开或切换调试 REPL（普通模式）
- `<Leader>db`：切换断点（普通模式）
- `<Leader>dc`：开始或继续调试（普通模式）
- `<Leader>dh`：查看调试悬浮信息（普通模式）
- `<Leader>di`：单步进入（普通模式）
- `<Leader>do`：单步跳过（普通模式）
- `<Leader>dp`：暂停调试（普通模式）
- `<Leader>dq`：关闭调试会话（普通模式）
- `<Leader>dr`：重启调试（普通模式）
- `<Leader>ds`：运行到光标处（普通模式）
- `<Leader>du`：切换调试界面（普通模式）

## 普通模式：终端与外部工具

- `<C-'>`：打开或切换终端（普通模式）
- `<F7>`：打开或切换终端（普通模式）
- `<Leader>tf`：打开或切换浮动终端（普通模式）
- `<Leader>th`：打开或切换水平终端（普通模式）
- `<Leader>tl`：打开或切换 lazygit 终端（普通模式）
- `<Leader>tn`：打开或切换 Node.js 终端（普通模式）
- `<Leader>tp`：打开或切换 Python 终端（普通模式）
- `<Leader>tt`：打开或切换 btm 终端（普通模式）
- `<Leader>tu`：打开或切换 gdu 终端（普通模式）
- `<Leader>tv`：打开或切换垂直终端（普通模式）

## 普通模式：插件与工具管理

- `<Leader>pM`：更新 Mason 工具（普通模式）
- `<Leader>pS`：同步插件（普通模式）
- `<Leader>pU`：更新插件（普通模式）
- `<Leader>pa`：同时更新 Lazy 和 Mason（普通模式）
- `<Leader>pi`：安装插件（普通模式）
- `<Leader>pm`：打开 Mason 安装器（普通模式）
- `<Leader>ps`：查看插件状态（普通模式）
- `<Leader>pu`：检查插件更新（普通模式）

## 普通模式：界面与功能开关

- `<Leader>u>`：切换折叠列（普通模式）
- `<Leader>uA`：切换 rooter 自动切目录（普通模式）
- `<Leader>uC`：切换全局自动补全（普通模式）
- `<Leader>uD`：清空当前通知（普通模式）
- `<Leader>uN`：切换通知功能（普通模式）
- `<Leader>uS`：切换 conceal 显示（普通模式）
- `<Leader>uV`：切换虚拟行诊断（普通模式）
- `<Leader>uZ`：切换专注模式（普通模式）
- `<Leader>ua`：切换自动配对（普通模式）
- `<Leader>ub`：切换背景模式（普通模式）
- `<Leader>uc`：切换当前缓冲区自动补全（普通模式）
- `<Leader>ud`：切换诊断显示（普通模式）
- `<Leader>ug`：切换符号列（普通模式）
- `<Leader>ui`：切换缩进设置（普通模式）
- `<Leader>ul`：切换状态栏（普通模式）
- `<Leader>un`：切换行号样式（普通模式）
- `<Leader>up`：切换粘贴模式（普通模式）
- `<Leader>ur`：切换引用高亮（普通模式）
- `<Leader>us`：切换拼写检查（普通模式）
- `<Leader>ut`：切换标签栏（普通模式）
- `<Leader>uu`：切换 URL 高亮（普通模式）
- `<Leader>uv`：切换虚拟文本诊断（普通模式）
- `<Leader>uw`：切换自动换行（普通模式）
- `<Leader>uy`：切换当前缓冲区语法高亮（普通模式）
- `<Leader>uz`：切换颜色高亮（普通模式）
- `<Leader>u|`：切换缩进参考线（普通模式）

## 普通模式：注释

- `<Leader>/`：切换当前行注释（普通模式）
- `gc`：切换注释（普通模式）
- `gcO`：在上方新增注释行（普通模式）
- `gcc`：切换当前行注释（普通模式）
- `gco`：在下方新增注释行（普通模式）

## 普通模式：导航、列表跳转与默认增强

- `%`：在匹配对象之间跳转（matchit 增强）（普通模式）
- `&`：Neovim 默认 `&` 行为，详见 `:help &-default`（普通模式）；当前右侧为 `:&&<CR>`
- `Y`：Neovim 默认 `Y` 行为，详见 `:help Y-default`（普通模式）；当前右侧为 `y$`
- `[%`：跳到上一个匹配块（matchit 增强）（普通模式）
- `[<C-L>`：跳到上一个 Location List 文件（普通模式）
- `[<C-Q>`：跳到上一个 Quickfix 文件（普通模式）
- `[<C-T>`：跳到上一个预览窗口条目（普通模式）
- `[<Space>`：在光标上方插入空行（普通模式）
- `[A`：跳到参数列表第一个条目（普通模式）
- `[D`：跳到当前缓冲区第一个诊断（普通模式）
- `[L`：跳到 Location List 第一个条目（普通模式）
- `[Q`：跳到 Quickfix 第一个条目（普通模式）
- `[T`：上一个 TODO 注释（普通模式）
- `[a`：跳到参数列表上一个条目（普通模式）
- `[d`：跳到当前缓冲区上一个诊断（普通模式）
- `[e`：上一个错误（普通模式）
- `[l`：跳到上一个 Location List 条目（普通模式）
- `[q`：跳到上一个 Quickfix 条目（普通模式）
- `[r`：上一个引用（普通模式）
- `[t`：上一个标签页（普通模式）
- `[w`：上一个警告（普通模式）
- `]%`：跳到下一个匹配块（matchit 增强）（普通模式）
- `]<C-L>`：跳到下一个 Location List 文件（普通模式）
- `]<C-Q>`：跳到下一个 Quickfix 文件（普通模式）
- `]<C-T>`：跳到下一个预览窗口条目（普通模式）
- `]<Space>`：在光标下方插入空行（普通模式）
- `]A`：跳到参数列表最后一个条目（普通模式）
- `]D`：跳到当前缓冲区最后一个诊断（普通模式）
- `]L`：跳到 Location List 最后一个条目（普通模式）
- `]Q`：跳到 Quickfix 最后一个条目（普通模式）
- `]T`：下一个 TODO 注释（普通模式）
- `]a`：跳到参数列表下一个条目（普通模式）
- `]d`：跳到当前缓冲区下一个诊断（普通模式）
- `]e`：下一个错误（普通模式）
- `]l`：跳到下一个 Location List 条目（普通模式）
- `]q`：跳到下一个 Quickfix 条目（普通模式）
- `]r`：下一个引用（普通模式）
- `]t`：下一个标签页（普通模式）
- `]w`：下一个警告（普通模式）
- `g%`：反向跳到匹配对象（matchit 增强）（普通模式）
- `gx`：用系统默认程序打开光标下的文件路径或 URI（普通模式）
- `j`：向下移动，软换行时按屏幕行移动（普通模式）
- `k`：向上移动，软换行时按屏幕行移动（普通模式）

## 可视模式

- `#`：Neovim 默认可视模式 `#` 行为，详见 `:help v_#-default`（可视模式）
- `%`：在匹配对象之间跳转（matchit 增强）（可视模式）
- `*`：Neovim 默认可视模式 `*` 行为，详见 `:help v_star-default`（可视模式）
- `<Leader>/`：切换注释（可视模式）
- `<Leader>dE`：执行调试表达式（可视模式）
- `<Leader>go`：打开当前仓库或文件的 Git 浏览页面（可视模式）
- `<S-Tab>`：反缩进选中行（可视模式）
- `<Tab>`：缩进选中行（可视模式）
- `@`：Neovim 默认可视模式 `@` 行为，详见 `:help v_@-default`（可视模式）；当前右侧为 `mode()<Space>==#<Space>'V'<Space>?<Space>':normal!<Space>@'.getcharstr().'<CR>'<Space>:<Space>'@'`
- `Q`：Neovim 默认可视模式 `Q` 行为，详见 `:help v_Q-default`（可视模式）；当前右侧为 `mode()<Space>==#<Space>'V'<Space>?<Space>':normal!<Space>@<C-R>=reg_recorded()<CR><CR>'<Space>:<Space>'Q'`
- `[%`：跳到上一个匹配块（matchit 增强）（可视模式）
- `]%`：跳到下一个匹配块（matchit 增强）（可视模式）
- `a%`：选中整个匹配块（matchit 增强）（可视模式）
- `g%`：反向跳到匹配对象（matchit 增强）（可视模式）
- `gc`：切换注释（可视模式）
- `gra`：代码操作（可视模式）
- `gx`：用系统默认程序打开光标下的文件路径或 URI（可视模式）
- `j`：向下移动，软换行时按屏幕行移动（可视模式）
- `k`：向上移动，软换行时按屏幕行移动（可视模式）

## 选择模式

- `<C-S>`：显示签名帮助（选择模式）
- `<Leader>dE`：执行调试表达式（选择模式）
- `<S-Tab>`：反缩进选中行（选择模式）
- `<Tab>`：缩进选中行（选择模式）

## 操作等待模式

- `%`：在匹配对象之间跳转（matchit 增强）（操作等待模式）
- `[%`：跳到上一个匹配块（matchit 增强）（操作等待模式）
- `]%`：跳到下一个匹配块（matchit 增强）（操作等待模式）
- `g%`：反向跳到匹配对象（matchit 增强）（操作等待模式）
- `gc`：注释文本对象（操作等待模式）

## 插入模式

- `<C-'>`：打开或切换终端（插入模式）
- `<C-S>`：显示签名帮助（插入模式）
- `<C-U>`：Neovim 默认插入模式 `<C-U>` 行为，详见 `:help i_CTRL-U-default`（插入模式）；当前右侧为 `<C-G>u<C-U>`
- `<C-W>`：Neovim 默认插入模式 `<C-W>` 行为，详见 `:help i_CTRL-W-default`（插入模式）；当前右侧为 `<C-G>u<C-W>`
- `<F7>`：打开或切换终端（插入模式）
- `<S-Tab>`：若存在活动片段则跳到上一个占位符，否则保留 `<S-Tab>` 默认行为（插入模式）
- `<Tab>`：若存在活动片段则跳到下一个占位符，否则保留 `<Tab>` 默认行为（插入模式）

## 终端模式

- `<C-'>`：打开或切换终端（终端模式）
- `<C-H>`：终端中跳到左侧窗口（终端模式）
- `<C-K>`：终端中跳到上方窗口（终端模式）
- `<C-L>`：终端中跳到右侧窗口（终端模式）
- `<F7>`：打开或切换终端（终端模式）
- `<NL>`：终端中跳到下方窗口（终端模式）

## 插件内部 `<Plug>` 映射

- `<Plug>(MatchitNormalBackward)`：插件内部映射（普通模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',0,'n')<CR>`
- `<Plug>(MatchitNormalForward)`：插件内部映射（普通模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',1,'n')<CR>`
- `<Plug>(MatchitNormalMultiBackward)`：插件内部映射（普通模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("bW",<Space>"n")<CR>`
- `<Plug>(MatchitNormalMultiForward)`：插件内部映射（普通模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("W",<Space><Space>"n")<CR>`
- `<Plug>(MatchitOperationBackward)`：插件内部映射（操作等待模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',0,'o')<CR>`
- `<Plug>(MatchitOperationForward)`：插件内部映射（操作等待模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',1,'o')<CR>`
- `<Plug>(MatchitOperationMultiBackward)`：插件内部映射（操作等待模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("bW",<Space>"o")<CR>`
- `<Plug>(MatchitOperationMultiForward)`：插件内部映射（操作等待模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("W",<Space><Space>"o")<CR>`
- `<Plug>(MatchitVisualBackward)`：插件内部映射（可视模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',0,'v')<CR>m'gv```
- `<Plug>(MatchitVisualForward)`：插件内部映射（可视模式）；当前右侧为 `:<C-U>call<Space>matchit#Match_wrapper('',1,'v')<CR>:if<Space>col("''")<Space>!=<Space>col("$")<Space>|<Space>exe<Space>":normal!<Space>m'"<Space>|<Space>endif<CR>gv```
- `<Plug>(MatchitVisualMultiBackward)`：插件内部映射（可视模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("bW",<Space>"n")<CR>m'gv```
- `<Plug>(MatchitVisualMultiForward)`：插件内部映射（可视模式）；当前右侧为 `:<C-U>call<Space>matchit#MultiMatch("W",<Space><Space>"n")<CR>m'gv```
- `<Plug>(MatchitVisualTextObject)`：插件内部映射（可视模式）；当前右侧为 `<Plug>(MatchitVisualMultiBackward)o<Plug>(MatchitVisualMultiForward)`
