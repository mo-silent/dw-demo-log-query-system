prompt: 所有的代码，注释，日志都使用英文

system: f"""

前端(vue.js 3.0)：

1. 搜索框，日志 label，时间搓

2. 搜索框下方的内容：默认为 app: main 的日志。

3. 用户通过搜索框，检索日志

后端(python+flask)：

1. 获取编写获取所有label 接口（grafana loki 日志label), 接口为 api/v1/loki/label

2. 接受前端Post 可选根据时间搓进行查询，必须 label, 接口为 api/v1/loki/logs, 参数都为 body

3. 推送自身日志到 loki(http://localhost:3100/loki/api/v1/push), label 为 `app: main`

4. 完整的单元测试，并且把单元测试日志推送到 loki

"""

user: 帮我完成这个日志查询系统