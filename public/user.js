// user.js - 修改注册逻辑
App.prototype.register = async function() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    // 验证输入
    if (!username || !email || !password) {
        utils.showNotification('请输入所有必填字段', 'error');
        return;
    }

    const loginBtn = document.getElementById('register-submit-btn');
    const loginText = document.getElementById('register-submit-text');
    const loginLoader = document.createElement('span');
    loginLoader.id = 'register-loader';
    loginLoader.className = 'loading';
    loginLoader.style.display = 'none';
    loginBtn.appendChild(loginLoader);

    utils.setButtonLoading(loginBtn, loginText, loginLoader, true);

    try {
        const result = await authService.register({ 
            username, 
            email, 
            password 
        });

        if (result.success) {
            utils.showNotification('注册成功！请登录', 'success');
            document.getElementById('register-modal').classList.remove('show');
        } else {
            // 解析错误信息
            let errorMessage = result.error;
            if (typeof result.error === 'object' && result.error !== null) {
                errorMessage = Object.values(result.error).join(', ');
            }
            utils.showNotification('注册失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        // 处理网络错误或其他异常
        let errorMessage = error.message;
        if (typeof error.message === 'object' && error.message !== null) {
            errorMessage = Object.values(error.message).join(', ');
        }
        utils.showNotification('注册失败: ' + errorMessage, 'error');
    } finally {
        utils.setButtonLoading(loginBtn, loginText, loginLoader, false);
    }
};