import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("计算器")
        master.configure(bg='#f0f0f0')
        master.resizable(False, False)
        
        # 显示框
        self.display = tk.Entry(master, width=20, font=('Arial', 16), bd=5, 
                               justify="right", bg="#e8e8e8")
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        # 存储计算的变量
        self.current_value = ""
        self.computation = ""
        self.result = False
        
        # 按钮布局
        button_layout = [
            ('C', 1, 0), ('⌫', 1, 1), ('%', 1, 2), ('/', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('±', 5, 2), ('=', 5, 3)
        ]
        
        # 创建按钮
        self.buttons = {}
        for (text, row, col) in button_layout:
            button = tk.Button(master, text=text, width=5, height=2, font=('Arial', 12))
            button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # 设置按钮颜色
            if text in ['C', '⌫', '%', '±']:
                button.configure(bg="#d9d9d9", fg="#000000")
            elif text in ['/', '*', '-', '+', '=']:
                button.configure(bg="#ff9500", fg="#000000")
            else:
                button.configure(bg="#e8e8e8", fg="#000000")
                
            # 绑定按钮事件
            if text == 'C':
                button.configure(command=self.clear_display)
            elif text == '⌫':
                button.configure(command=self.backspace)
            elif text == '=':
                button.configure(command=self.calculate)
            elif text == '±':
                button.configure(command=self.toggle_sign)
            else:
                # 为所有其他按钮（包括运算符）使用相同的绑定方式，但确保每个按钮捕获自己的文本
                button.configure(command=lambda t=text: self.add_to_display(t))
                
            self.buttons[text] = button
        
        # 配置网格权重，使按钮可以随窗口调整大小
        for i in range(6):
            master.grid_rowconfigure(i, weight=1)
        for i in range(4):
            master.grid_columnconfigure(i, weight=1)
            
        # 绑定键盘事件
        master.bind('<Return>', lambda event: self.calculate())
        master.bind('<BackSpace>', lambda event: self.backspace())
        master.bind('<Escape>', lambda event: self.clear_display())
        
        # 数字键绑定
        for key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            master.bind(key, lambda event, digit=key: self.add_to_display(digit))
        
        # 运算符键绑定
        master.bind('+', lambda event: self.add_to_display('+'))
        master.bind('-', lambda event: self.add_to_display('-'))
        master.bind('*', lambda event: self.add_to_display('*'))
        master.bind('/', lambda event: self.add_to_display('/'))
        master.bind('%', lambda event: self.add_to_display('%'))
    
    def add_to_display(self, value):
        if self.result:
            # 如果刚显示过结果，则清空显示框
            self.current_value = ""
            self.result = False
        
        self.current_value += value
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_value)
    
    def clear_display(self):
        self.current_value = ""
        self.computation = ""
        self.display.delete(0, tk.END)
    
    def backspace(self):
        self.current_value = self.current_value[:-1]
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_value)
    
    def toggle_sign(self):
        if self.current_value and self.current_value[0] == '-':
            self.current_value = self.current_value[1:]
        else:
            self.current_value = '-' + self.current_value
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_value)
    
    def calculate(self):
        try:
            # 替换显示的%为/100进行计算
            expression = self.current_value.replace('%', '/100')
            result = eval(expression)
            
            # 如果结果是整数，不显示小数点
            if result == int(result):
                result = int(result)
                
            self.display.delete(0, tk.END)
            self.display.insert(0, str(result))
            self.current_value = str(result)
            self.result = True
        except Exception as e:
            messagebox.showerror("错误", "计算错误: " + str(e))
            self.clear_display()

def main():
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()