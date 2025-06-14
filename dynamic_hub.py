class Hub4to1:
    """
    4输入1输出空信号传递 - 输入任何数据，输出字符串"0"
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "输入_1": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": None}),
                "输入_2": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": None}),
                "输入_3": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": None}),
                "输入_4": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": None}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("输出",)
    OUTPUT_NODE = False
    FUNCTION = "process"
    CATEGORY = "自动数据"
    
    def process(self, **kwargs):
        return ("0",)


class Hub1to4:
    """
    1输入4输出空信号传递 - 输入任何数据，输出4个字符串"0"
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "输入": ("IMAGE,MASK,LATENT,MODEL,CLIP,VAE,CONDITIONING,STRING,INT,FLOAT", {"default": None}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("输出_1", "输出_2", "输出_3", "输出_4")
    OUTPUT_NODE = False
    FUNCTION = "process"
    CATEGORY = "自动数据"
    
    def process(self, **kwargs):
        return ("0", "0", "0", "0")


# 注册节点
NODE_CLASS_MAPPINGS = {
    "Hub4to1": Hub4to1,
    "Hub1to4": Hub1to4,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Hub4to1": "4转1空信号传递[自动数据]",
    "Hub1to4": "1转4空信号传递[自动数据]",
}