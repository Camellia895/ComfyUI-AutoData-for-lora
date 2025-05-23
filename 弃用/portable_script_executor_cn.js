// portable_script_executor_cn.js
import { app } from "/scripts/app.js"; // ComfyUI app instance
import { api } from "/scripts/api.js";   // ComfyUI api instance

// 确保节点类型名称与Python中 NODE_CLASS_MAPPINGS 的键一致，或者 Python 中定义的 NAME 属性
const NODE_TYPE_NAME = "便携脚本执行器_JS动态接口"; 

app.registerExtension({
    name: "Comfy.PortableScriptExecutorJSCN", // 给你的扩展起一个唯一的名字
    
    // 当节点类型被注册后，可以对其进行扩展
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === NODE_TYPE_NAME) {
            // console.log(`扩展节点: ${nodeData.name}`);

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                // 调用原始的 onNodeCreated (如果存在)
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // this 指向当前的节点实例
                // console.log("便携脚本执行器 (JS) onNodeCreated", this);

                // 创建一个用于存放动态生成控件的容器
                this.dynamicWidgetsContainer = document.createElement("div");
                this.dynamicWidgetsContainer.className = "comfy-dynamic-widgets-container";
                // 将容器添加到节点的widgets区域 (如果节点有widgets) 或直接添加到节点元素
                // LiteGraph节点没有标准的 widget 区域，我们需要自己管理DOM
                // this.root.appendChild(this.dynamicWidgetsContainer); // this.root 是 LGraphCanvas 的根SVG，不适合直接加控件
                // 我们需要找到节点的HTML元素，或者在 onDrawForeground 中绘制
                // 更简单的方式是，如果节点有Python定义的widgets，我们可以尝试添加到那里。
                // 但我们的Python节点目前没有输出型widgets。

                // 先找到 "选择脚本" 这个widget
                const scriptSelectorWidget = this.widgets.find(w => w.name === "选择脚本");
                if (scriptSelectorWidget) {
                    // console.log("找到脚本选择器 widget:", scriptSelectorWidget);
                    const originalCallback = scriptSelectorWidget.callback;
                    scriptSelectorWidget.callback = (value, LGraphCanvas, node, LGraphNode, event) => {
                        if (originalCallback) {
                            originalCallback.call(this, value, LGraphCanvas, node, LGraphNode, event);
                        }
                        // console.log(`脚本已选择: ${value}, 节点ID: ${this.id}`);
                        this.updateDynamicInputs(value); // 当脚本选择改变时，更新动态输入
                    };
                }

                // 初始化时也尝试更新一次 (如果已有选择)
                if (scriptSelectorWidget && scriptSelectorWidget.value && scriptSelectorWidget.value !== "未找到脚本") {
                    this.updateDynamicInputs(scriptSelectorWidget.value);
                }
                return r;
            };

            // 添加一个方法到节点原型上，用于更新动态输入
            nodeType.prototype.updateDynamicInputs = async function (scriptName) {
                // console.log(`请求脚本 '${scriptName}' 的参数... 节点ID: ${this.id}`);
                if (scriptName === "未找到脚本") {
                    this.clearDynamicInputs();
                    return;
                }

                try {
                    // 调用后端API获取参数定义
                    // 注意：api.fetchApi 的路径是相对于 / 的
                    const paramsDefinition = await api.fetchApi(
                        `/comfy_portable_script_executor/get_script_params?script_name=${encodeURIComponent(scriptName)}`, 
                        { method: "GET", cache: "no-store" }
                    );
                    // console.log("从API获取到的参数定义:", paramsDefinition);

                    if (paramsDefinition && paramsDefinition.parameters) {
                        this.generateDynamicInputs(paramsDefinition.parameters);
                    } else if (paramsDefinition && paramsDefinition.error) {
                        console.error(`获取脚本参数失败: ${paramsDefinition.error}`);
                        this.clearDynamicInputs();
                        // 可以在节点上显示错误信息
                        this.addProperty("script_error", `错误: ${paramsDefinition.error}`, "STRING");
                    } else {
                        this.clearDynamicInputs();
                         if (this.hasProperty("script_error")) this.removeProperty("script_error");
                    }
                } catch (error) {
                    console.error("调用API /get_script_params 失败:", error);
                    this.clearDynamicInputs();
                    this.addProperty("script_error", `API调用失败: ${error.message}`, "STRING");
                }
                this.setDirtyCanvas(true, true); // 请求重绘画布
            };

            // 清除动态生成的输入
            nodeType.prototype.clearDynamicInputs = function() {
                // console.log("清除动态输入...", this.id);
                if (this.dynamicInputs && this.dynamicInputs.length > 0) {
                    this.dynamicInputs.forEach(widget => {
                        if (this.widgets.includes(widget)) {
                            this.widgets.splice(this.widgets.indexOf(widget), 1);
                        }
                    });
                    this.dynamicInputs = [];
                }
                 // 更新隐藏的 dynamic_params_json widget 的值
                const hiddenParamsWidget = this.widgets.find(w => w.name === "dynamic_params_json");
                if (hiddenParamsWidget) {
                    hiddenParamsWidget.value = "{}";
                }
                if (this.hasProperty("script_error")) this.removeProperty("script_error");
                this.computeSize(); // 重新计算节点大小
                this.setDirtyCanvas(true, true);
            };

            // 根据参数定义生成动态输入控件
            nodeType.prototype.generateDynamicInputs = function (parameters) {
                this.clearDynamicInputs(); // 先清除旧的
                // console.log("生成动态输入基于:", parameters, "节点ID:", this.id);
                this.dynamicInputs = []; // 存储动态创建的widgets，方便管理

                const currentDynamicParams = {};

                parameters.forEach(param => {
                    let widget = null;
                    const widgetName = `dyn_${param.name}`; // 给动态widget一个唯一的名字
                    const widgetLabel = param.label_cn || param.name;

                    // LiteGraph 没有直接的 "label" widget，标签通常是 widget name 的一部分
                    // 或者在 onDrawForeground 中绘制。
                    // 我们这里将标签作为 widget 的 name/label 属性 (如果 widget 支持)
                    // 或者作为 widget 的一部分。

                    // ComfyUI widget 的创建方式: this.addWidget(type, name, value, callback, options)
                    if (param.type === "STRING") {
                        widget = this.addWidget("text", widgetLabel, param.default || "", (value) => {
                            currentDynamicParams[param.name] = value;
                            this.updateHiddenParamsJSON(currentDynamicParams);
                        }, { multiline: param.multiline || false });
                    } else if (param.type === "INT") {
                        widget = this.addWidget("number", widgetLabel, param.default || 0, (value) => {
                            currentDynamicParams[param.name] = parseInt(value, 10);
                            this.updateHiddenParamsJSON(currentDynamicParams);
                        }, { min: param.min, max: param.max, step: param.step || 1, precision: 0 });
                    } else if (param.type === "FLOAT") {
                         widget = this.addWidget("number", widgetLabel, param.default || 0.0, (value) => {
                            currentDynamicParams[param.name] = parseFloat(value);
                            this.updateHiddenParamsJSON(currentDynamicParams);
                        }, { min: param.min, max: param.max, step: param.step || 0.01, precision: 2 }); // precision 调整
                    } else if (param.type === "BOOLEAN") {
                        widget = this.addWidget("toggle", widgetLabel, param.default || false, (value) => {
                            currentDynamicParams[param.name] = value;
                            this.updateHiddenParamsJSON(currentDynamicParams);
                        });
                    } else if (param.type === "COMBO" && param.options) {
                        widget = this.addWidget("combo", widgetLabel, param.default || param.options[0], (value) => {
                             currentDynamicParams[param.name] = value;
                             this.updateHiddenParamsJSON(currentDynamicParams);
                        }, { values: param.options });
                    }
                    // ... 可以添加更多类型如 COLOR, VEC2 等，如果 LiteGraph/Comfy 支持的话

                    if (widget) {
                        widget.dynamic = true; // 加个标记
                        this.dynamicInputs.push(widget);
                        currentDynamicParams[param.name] = widget.value; // 初始化
                    }
                });

                this.updateHiddenParamsJSON(currentDynamicParams); // 初始化一次隐藏参数
                this.computeSize(); // 重新计算节点大小以适应新的widgets
                this.setDirtyCanvas(true, true);
            };

            // 更新隐藏的 dynamic_params_json widget 的值
            nodeType.prototype.updateHiddenParamsJSON = function(paramsObject) {
                const hiddenParamsWidget = this.widgets.find(w => w.name === "dynamic_params_json");
                if (hiddenParamsWidget) {
                    hiddenParamsWidget.value = JSON.stringify(paramsObject);
                    // console.log(`Updated hidden_params_json: ${hiddenParamsWidget.value}`);
                }
            };

            // 当节点从图上移除时，清理工作 (如果需要)
            // const onRemoved = nodeType.prototype.onRemoved;
            // nodeType.prototype.onRemoved = function() {
            //     this.clearDynamicInputs();
            //     if (onRemoved) {
            //         onRemoved.apply(this, arguments);
            //     }
            // };
        }
    },
});

console.log("便携脚本执行器 (JS动态接口) JavaScript部分已加载。");