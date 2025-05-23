// prompt_selector/js/prompt_selector.js
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.PromptSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "PromptSelector") {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        
        nodeType.prototype.onNodeCreated = function() {
            const node = this;
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }
            
            const promptWidget = this.widgets.find(w => w.name === "prompt_pairs");
            const keyWidget = this.widgets.find(w => w.name === "selected_key");
            
            if (promptWidget && keyWidget) {

                promptWidget.callback = (value) => {
                    const keys = parsePromptPairs(value);
                    updateKeyWidget(keyWidget, keys);
                    node.setDirtyCanvas(true, true);

                    //update_psn_server_keys(node.id, JSON.stringify(keys));
                };
            
                // 初始化时触发一次回调
                promptWidget.callback(promptWidget.value);
            }
        };

        // 配置加载后的初始化
        nodeType.prototype.onConfigure = function() {
            const promptWidget = this.widgets.find(w => w.name === "prompt_pairs");
            const keyWidget = this.widgets.find(w => w.name === "selected_key");
            
            if (promptWidget?.value && keyWidget) {
                const keys = parsePromptPairs(promptWidget.value);
                updateKeyWidget(keyWidget, keys);
            }
        };
    }
});

function updateKeyWidget(keyWidget, keys) {
    // 更新选项列表
    keyWidget.options.values = keys;
    
    // 如果当前值不在新的选项列表中，设置为第一个选项
    if (!keys.includes(keyWidget.value)) {
        keyWidget.value = keys[0];
    }
    
    // 通知ComfyUI更新widget状态
    if (keyWidget.callback) {
        keyWidget.callback(keyWidget.value);
    }
}

function parsePromptPairs(text) {
    if (!text?.trim()) {
        return ["key1"];
    }
    
    try {
        const normalizedText = text.replace(/\n/g, '');
        const pairs = normalizedText.split(",")
            .filter(pair => pair.trim());
            
        const keys = [];
        
        for (const pair of pairs) {
            if (pair.includes('":"')) {
                const [key] = pair.split('":"')
                    .map(part => part.trim().replace(/^"|"$/g, ''));
                if (key) {
                    keys.push(key);
                }
            }
        }
        
        return keys.length > 0 ? keys : ["key1"];
    } catch (error) {
        console.error("解析提示词对时出错:", error);
        return ["key1"];
    }
}

function update_psn_server_keys(node_id, message) {
    const body = new FormData();
    body.append('message',message);
    body.append('node_id',node_id);
    api.fetchApi("/update_psn_keys", { method: "POST", body, });
}