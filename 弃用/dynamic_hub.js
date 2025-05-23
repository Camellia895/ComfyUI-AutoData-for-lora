// 简单的调试函数
function debugLog(message) {
    console.log(`[DataHub-DEBUG] ${message}`);
    // 同时输出到页面标题，这样更容易看到
    if (typeof document !== 'undefined') {
        document.title = `ComfyUI - ${message}`;
    }
}

debugLog("JavaScript文件开始执行");

// 检查app是否存在
if (typeof app === 'undefined') {
    debugLog("错误: app对象不存在，尝试导入");
    try {
        const { app } = await import("../../scripts/app.js");
        debugLog("成功导入app对象");
    } catch (e) {
        debugLog(`导入失败: ${e.message}`);
    }
}

// 尝试注册扩展
try {
    debugLog("开始注册扩展");
    
    // 确保app存在
    const appModule = await import("../../scripts/app.js");
    const { app } = appModule;
    
    debugLog("成功获取app对象，开始注册");
    
    app.registerExtension({
        name: "DataHub.Extension",
        
        async beforeRegisterNodeDef(nodeType, nodeData, app) {
            debugLog(`检查节点: ${nodeData.name}`);
            
            if (nodeData.name === "DataHub") {
                debugLog("找到DataHub节点！开始处理");
                
                // 保存原始方法
                const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
                
                // 重写节点创建方法
                nodeType.prototype.onNodeCreated = function() {
                    debugLog("DataHub节点被创建");
                    
                    // 执行原始创建逻辑
                    const result = originalOnNodeCreated ? originalOnNodeCreated.apply(this, arguments) : undefined;
                    
                    // 添加我们的逻辑
                    this.hideUnusedPorts = function() {
                        const inputCount = this.widgets?.find(w => w.name === "输入数量")?.value || 3;
                        const outputCount = this.widgets?.find(w => w.name === "输出数量")?.value || 3;
                        
                        debugLog(`更新端口显示: 输入${inputCount}个, 输出${outputCount}个`);
                        
                        // 隐藏多余的输入
                        if (this.inputs) {
                            for (let i = 0; i < this.inputs.length; i++) {
                                const input = this.inputs[i];
                                if (input.name && input.name.startsWith("输入_")) {
                                    const portNum = parseInt(input.name.split("_")[1]);
                                    input.hidden = portNum > inputCount;
                                }
                            }
                        }
                        
                        // 隐藏多余的输出
                        if (this.outputs) {
                            for (let i = 0; i < this.outputs.length; i++) {
                                const output = this.outputs[i];
                                if (output.name && output.name.startsWith("输出_")) {
                                    const portNum = parseInt(output.name.split("_")[1]);
                                    output.hidden = portNum > outputCount;
                                }
                            }
                        }
                        
                        // 重新计算大小
                        this.setSize(this.computeSize());
                    };
                    
                    // 初始化端口显示
                    setTimeout(() => {
                        this.hideUnusedPorts();
                    }, 100);
                    
                    return result;
                };
                
                // 重写参数变化方法
                const originalOnWidgetChanged = nodeType.prototype.onWidgetChanged;
                nodeType.prototype.onWidgetChanged = function(name, value, old_value, widget) {
                    debugLog(`参数变化: ${name} = ${value}`);
                    
                    const result = originalOnWidgetChanged ? originalOnWidgetChanged.apply(this, arguments) : undefined;
                    
                    if (name === "输入数量" || name === "输出数量") {
                        debugLog("触发端口更新");
                        setTimeout(() => {
                            if (this.hideUnusedPorts) {
                                this.hideUnusedPorts();
                            }
                        }, 50);
                    }
                    
                    return result;
                };
                
                debugLog("DataHub扩展注册完成");
            }
        }
    });
    
    debugLog("扩展注册成功！");
    
} catch (error) {
    debugLog(`扩展注册失败: ${error.message}`);
    console.error("DataHub扩展错误:", error);
}