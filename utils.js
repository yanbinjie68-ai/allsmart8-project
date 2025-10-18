// utils.js - 确保通知函数正确
const utils = {
    showNotification: function(message, type) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 3秒后自动隐藏
        setTimeout(() => {
            notification.remove();
        }, 3000);
    },
    
    setButtonLoading: function(button, originalText, loaderElement, isLoading) {
        if (isLoading) {
            button.textContent = '注册中...';
            loaderElement.style.display = 'inline-block';
            button.disabled = true;
        } else {
            button.textContent = originalText;
            loaderElement.style.display = 'none';
            button.disabled = false;
        }
    }
};