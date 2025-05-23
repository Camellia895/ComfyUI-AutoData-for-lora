class UniversalHub:
    """
    通用数据中转节点 - 可以动态调整输入输出数量
    支持任意数据类型的传递
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "输入数量": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "display": "number"
                }),
                "输出数量": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "display": "number"
                }),
            },
            "optional": {}
        }
    
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("输出",)
    OUTPUT_NODE = False
    FUNCTION = "process"
    CATEGORY = "工具/数据处理"
    
    def process(self, 输入数量=1, 输出数量=1, **kwargs):
        """
        处理数据传递
        """
        # 收集所有输入的数据
        inputs = []
        for i in range(输入数量):
            input_key = f"输入_{i+1}"
            if input_key in kwargs:
                inputs.append(kwargs[input_key])
            else:
                # 如果没有输入，提供默认值
                inputs.append(0)
        
        # 根据输出数量返回数据
        if 输出数量 == 0:
            return ()
        elif 输出数量 == 1:
            # 如果只有一个输出，返回第一个输入或默认值
            return (inputs[0] if inputs else 0,)
        else:
            # 多个输出时，循环使用输入数据或填充默认值
            outputs = []
            for i in range(输出数量):
                if i < len(inputs):
                    outputs.append(inputs[i])
                else:
                    # 如果输出数量超过输入数量，循环使用输入或使用默认值
                    if inputs:
                        outputs.append(inputs[i % len(inputs)])
                    else:
                        outputs.append(0)
            return tuple(outputs)


class UniversalHubDynamic:
    """
    动态通用数据中转节点 - 运行时动态生成输入输出
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # 基础配置输入
        base_inputs = {
            "required": {
                "输入数量": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
                "输出数量": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
            },
            "optional": {}
        }
        
        # 动态添加最大数量的输入端口
        for i in range(10):
            base_inputs["optional"][f"输入_{i+1}"] = ("*", {"default": None})
        
        return base_inputs
    
    RETURN_TYPES = tuple(["*"] * 10)  # 最大10个输出
    RETURN_NAMES = tuple([f"输出_{i+1}" for i in range(10)])
    OUTPUT_NODE = False
    FUNCTION = "process"
    CATEGORY = "工具/数据处理"
    
    def process(self, 输入数量=1, 输出数量=1, **kwargs):
        """
        动态处理数据传递
        """
        # 收集实际的输入数据
        inputs = []
        for i in range(输入数量):
            input_key = f"输入_{i+1}"
            if input_key in kwargs and kwargs[input_key] is not None:
                inputs.append(kwargs[input_key])
        
        # 生成输出
        outputs = []
        for i in range(10):  # 最大输出数量
            if i < 输出数量:
                if i < len(inputs):
                    outputs.append(inputs[i])
                else:
                    # 如果输出数量超过输入数量，循环使用或提供默认值
                    if inputs:
                        outputs.append(inputs[i % len(inputs)])
                    else:
                        outputs.append(0)
            else:
                # 超出指定输出数量的端口返回None
                outputs.append(None)
        
        return tuple(outputs)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "通用中转节点": UniversalHub,
    "动态中转节点": UniversalHubDynamic,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "通用中转节点": "通用中转节点 Universal Hub",
    "动态中转节点": "动态中转节点 Dynamic Hub",
}