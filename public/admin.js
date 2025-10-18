// 在admin.js中添加以下函数
// admin.js
App.prototype.loadEnvPreview = async function() {
    try {
        const response = await fetch('/api/env-preview');
        const envData = await response.json();
        document.getElementById('env-preview').textContent = JSON.stringify(envData, null, 2);
    } catch (error) {
        utils.showNotification('加载 .env 预览失败: ' + error.message, 'error');
    }
};

App.prototype.loadApiConfig = async function(configId) {
    try {
        const response = await fetch(`/api/api-configs/${configId}`);
        if (response.ok) {
            const configData = await response.json();
            
            // 填充表单字段
            document.getElementById('api-config-id').value = configData.id;
            document.getElementById('api-name').value = configData.name;
            document.getElementById('api-endpoint').value = configData.endpoint;
            document.getElementById('api-method').value = configData.method || 'GET';
            document.getElementById('api-description').value = configData.description || '';
            document.getElementById('api-authType').value = configData.auth_type || '';
            document.getElementById('api-provider').value = configData.provider || '';
            document.getElementById('api-category').value = configData.category || '';
            document.getElementById('api-max-requests').value = configData.max_requests || '';
            document.getElementById('api-priority').value = configData.priority || '';
            document.getElementById('api-active').checked = configData.is_active;
            document.getElementById('api-public').checked = configData.is_public;
            
            // 更新按钮文本
            document.getElementById('api-submit-btn').textContent = '更新API配置';
            document.getElementById('api-cancel-btn').style.display = 'inline-block';
            
            this.isEditing = true;
            this.currentEditId = configId;
        } else {
            utils.showNotification('加载API配置失败', 'error');
        }
    } catch (error) {
        utils.showNotification('加载API配置时发生错误: ' + error.message, 'error');
    }
};

// 修改editApiConfig函数
App.prototype.editApiConfig = function(configId) {
    // 加载API配置数据
    this.loadApiConfig(configId);
};

// admin.js - 修改 saveApiConfig 函数
App.prototype.saveApiConfig = async function() {
    try {
        const formData = new FormData(document.getElementById('api-config-form'));
        const apiConfigData = {};
        
        // 收集表单数据
        apiConfigData.name = formData.get('name');
        apiConfigData.endpoint = formData.get('endpoint');
        apiConfigData.method = formData.get('method');
        apiConfigData.description = formData.get('description');
        apiConfigData.auth_type = formData.get('authType');
        apiConfigData.provider = formData.get('provider');
        apiConfigData.category = formData.get('category');
        apiConfigData.max_requests = parseInt(formData.get('maxRequests')) || 1000;
        apiConfigData.priority = parseInt(formData.get('priority')) || 2;
        apiConfigData.is_active = formData.get('isActive') === 'on';
        apiConfigData.is_public = formData.get('isPublic') === 'on';
        apiConfigData.api_key = formData.get('apiKey');
        
        // 发送请求到后端
        const response = await fetch('/api/api-configs' + (this.isEditing ? '/' + this.currentEditId : ''), {
            method: this.isEditing ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(apiConfigData)
        });
        
        if (response.ok) {
            const result = await response.json();
            utils.showNotification('API配置保存成功', 'success');
            
            // 重置表单
            this.resetForm();
            
            // 刷新列表
            this.loadApiConfigs();
        } else {
            const errorData = await response.json();
            utils.showNotification(`保存API配置失败: ${errorData.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        utils.showNotification(`保存API配置时发生错误: ${error.message}`, 'error');
    }
};

// 添加重置表单方法
App.prototype.resetForm = function() {
    document.getElementById('api-config-form').reset();
    document.getElementById('api-config-id').value = '';
    document.getElementById('api-submit-btn').textContent = '添加API配置';
    document.getElementById('api-cancel-btn').style.display = 'none';
    this.isEditing = false;
    this.currentEditId = null;
};

// admin.js - 修改后的版本
App.prototype.loadUsers = async function() {
    try {
        const response = await fetch('/api/users', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const users = await response.json();
            // 渲染用户列表
            this.renderUsers(users);
        } else {
            throw new Error('获取用户列表失败');
        }
    } catch (error) {
        utils.showNotification('加载用户列表失败: ' + error.message, 'error');
    }
};

App.prototype.renderUsers = function(users) {
    const userListContainer = document.getElementById('user-list');
    
    if (!users || users.length === 0) {
        userListContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-users"></i>
                <p>暂无用户信息</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    users.forEach(user => {
        html += `
            <div class="user-item" data-user-id="${user.id}">
                <div class="user-info">
                    <h4>${user.username}</h4>
                    <p>${user.email}</p>
                    <span class="user-role">${user.role}</span>
                    <span class="user-status ${user.is_active ? 'status-active' : 'status-inactive'}">
                        ${user.is_active ? '活跃' : '禁用'}
                    </span>
                </div>
                <div class="user-actions">
                    <button class="btn btn-primary edit-user-btn" data-user-id="${user.id}">编辑</button>
                    <button class="btn btn-danger delete-user-btn" data-user-id="${user.id}">删除</button>
                </div>
            </div>
        `;
    });
    
    userListContainer.innerHTML = html;
    
    // 绑定编辑和删除事件
    this.bindUserActions();
};

App.prototype.bindUserActions = function() {
    // 绑定编辑按钮点击事件
    document.querySelectorAll('.edit-user-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.target.getAttribute('data-user-id');
            this.editUser(userId);
        });
    });
    
    // 绑定删除按钮点击事件
    document.querySelectorAll('.delete-user-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.target.getAttribute('data-user-id');
            this.deleteUser(userId);
        });
    });
};

App.prototype.editUser = async function(userId) {
    try {
        // 获取用户详细信息
        const response = await fetch(`/api/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            // 显示编辑模态框
            this.showEditUserModal(user);
        } else {
            throw new Error('获取用户信息失败');
        }
    } catch (error) {
        utils.showNotification('获取用户信息失败: ' + error.message, 'error');
    }
};

App.prototype.showEditUserModal = function(user) {
    // 创建或更新模态框
    let modal = document.getElementById('edit-user-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'edit-user-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <h2>编辑用户</h2>
                <form id="edit-user-form">
                    <input type="hidden" id="edit-user-id">
                    <div class="form-group">
                        <label for="edit-username">用户名</label>
                        <input type="text" id="edit-username" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-email">邮箱</label>
                        <input type="email" id="edit-email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-role">角色</label>
                        <select id="edit-role" class="form-control">
                            <option value="user">用户</option>
                            <option value="admin">管理员</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="edit-is-active">
                            <span class="checkmark">账户活跃</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <button type="button" id="save-user-btn" class="btn btn-primary">保存</button>
                        <button type="button" id="cancel-user-btn" class="btn btn-secondary">取消</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        // 绑定关闭事件
        modal.querySelector('.close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // 绑定取消按钮事件
        document.getElementById('cancel-user-btn').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // 绑定保存按钮事件
        document.getElementById('save-user-btn').addEventListener('click', () => {
            const userId = document.getElementById('edit-user-id').value;
            this.saveUser(userId);
        });
    }
    
    // 填充表单数据
    document.getElementById('edit-user-id').value = user.id;
    document.getElementById('edit-username').value = user.username;
    document.getElementById('edit-email').value = user.email;
    document.getElementById('edit-role').value = user.role;
    document.getElementById('edit-is-active').checked = user.is_active;
    
    // 显示模态框
    modal.style.display = 'block';
};

App.prototype.saveUser = async function(userId) {
    try {
        const username = document.getElementById('edit-username').value;
        const email = document.getElementById('edit-email').value;
        const role = document.getElementById('edit-role').value;
        const is_active = document.getElementById('edit-is-active').checked;
        
        const userData = { username, email, role, is_active };
        
        // 发送更新请求
        const response = await fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            utils.showNotification('用户信息更新成功', 'success');
            this.loadUsers(); // 重新加载用户列表
            document.getElementById('edit-user-modal').style.display = 'none'; // 关闭模态框
        } else {
            const errorData = await response.json();
            utils.showNotification(`更新用户失败: ${errorData.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        utils.showNotification(`更新用户时发生错误: ${error.message}`, 'error');
    }
};

App.prototype.deleteUser = async function(userId) {
    try {
        if (confirm('确定要删除这个用户吗？')) {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                utils.showNotification('用户删除成功', 'success');
                this.loadUsers(); // 重新加载用户列表
            } else {
                const errorData = await response.json();
                utils.showNotification(`删除用户失败: ${errorData.detail || '未知错误'}`, 'error');
            }
        }
    } catch (error) {
        utils.showNotification(`删除用户时发生错误: ${error.message}`, 'error');
    }
};

// 添加加载管理员列表的方法
App.prototype.loadAdmins = async function() {
    try {
        const response = await fetch('/api/admins', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const admins = await response.json();
            // 渲染管理员列表
            this.renderAdmins(admins);
        } else {
            throw new Error('获取管理员列表失败');
        }
    } catch (error) {
        utils.showNotification('加载管理员列表失败: ' + error.message, 'error');
    }
};

// 添加渲染管理员列表的方法
App.prototype.renderAdmins = function(admins) {
    const adminListContainer = document.getElementById('admin-list');
    
    if (!admins || admins.length === 0) {
        adminListContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-shield"></i>
                <p>暂无管理员信息</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    admins.forEach(admin => {
        html += `
            <div class="device-item">
                <div class="device-info">
                    <h3>${admin.username}</h3>
                    <p>角色: ${admin.role}</p>
                    <p>创建时间: ${new Date(admin.created_at).toLocaleString()}</p>
                </div>
                <div class="device-actions">
                    <button class="btn btn-sm btn-warning edit-admin-btn" data-admin-id="${admin.id}">编辑</button>
                    <button class="btn btn-sm btn-danger delete-admin-btn" data-admin-id="${admin.id}" ${admin.username === 'admin' ? 'disabled' : ''}>删除</button>
                </div>
            </div>
        `;
    });
    
    adminListContainer.innerHTML = html;
    
    // 绑定编辑和删除事件
    this.bindAdminActions();
};

// 添加绑定管理员操作事件的方法
App.prototype.bindAdminActions = function() {
    // 绑定编辑按钮点击事件
    document.querySelectorAll('.edit-admin-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const adminId = e.target.getAttribute('data-admin-id');
            this.editAdmin(adminId);
        });
    });
    
    // 绑定删除按钮点击事件
    document.querySelectorAll('.delete-admin-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const adminId = e.target.getAttribute('data-admin-id');
            this.deleteAdmin(adminId);
        });
    });
};

// 添加编辑管理员的方法
App.prototype.editAdmin = async function(adminId) {
    try {
        // 获取管理员详细信息
        const response = await fetch(`/api/admins/${adminId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const admin = await response.json();
            // 显示编辑模态框
            this.showEditAdminModal(admin);
        } else {
            throw new Error('获取管理员信息失败');
        }
    } catch (error) {
        utils.showNotification('获取管理员信息失败: ' + error.message, 'error');
    }
};

// 添加显示编辑管理员模态框的方法
App.prototype.showEditAdminModal = function(admin) {
    // 创建或更新模态框
    let modal = document.getElementById('edit-admin-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'edit-admin-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <h2>编辑管理员</h2>
                <form id="edit-admin-form">
                    <input type="hidden" id="edit-admin-id">
                    <div class="form-group">
                        <label for="edit-admin-username">用户名</label>
                        <input type="text" id="edit-admin-username" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="edit-admin-password">新密码 (留空则不修改)</label>
                        <input type="password" id="edit-admin-password" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="edit-admin-role">角色</label>
                        <select id="edit-admin-role" class="form-control">
                            <option value="admin">管理员</option>
                            <option value="superadmin">超级管理员</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="button" id="save-admin-btn" class="btn btn-primary">保存</button>
                        <button type="button" id="cancel-admin-btn" class="btn btn-secondary">取消</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        
        // 绑定关闭事件
        modal.querySelector('.close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        // 绑定取消按钮事件
        document.getElementById('cancel-admin-btn').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    // 填充表单数据
    document.getElementById('edit-admin-id').value = admin.id;
    document.getElementById('edit-admin-username').value = admin.username;
    document.getElementById('edit-admin-role').value = admin.role;
    
    // 清空密码字段
    document.getElementById('edit-admin-password').value = '';
    
    // 显示模态框
    modal.style.display = 'block';
    
    // 绑定保存按钮事件
    document.getElementById('save-admin-btn').onclick = () => {
        this.saveAdmin(admin.id);
    };
};

// 添加保存管理员的方法
App.prototype.saveAdmin = async function(adminId) {
    try {
        const username = document.getElementById('edit-admin-username').value;
        const password = document.getElementById('edit-admin-password').value;
        const role = document.getElementById('edit-admin-role').value;
        
        const adminData = { username, role };
        if (password) {
            adminData.password = password;
        }
        
        // 发送更新请求
        const response = await fetch(`/api/admins/${adminId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(adminData)
        });
        
        if (response.ok) {
            utils.showNotification('管理员信息更新成功', 'success');
            this.loadAdmins(); // 重新加载管理员列表
            document.getElementById('edit-admin-modal').style.display = 'none'; // 关闭模态框
        } else {
            const errorData = await response.json();
            utils.showNotification(`更新管理员失败: ${errorData.detail || '未知错误'}`, 'error');
        }
    } catch (error) {
        utils.showNotification(`更新管理员时发生错误: ${error.message}`, 'error');
    }
};

// 添加删除管理员的方法
App.prototype.deleteAdmin = async function(adminId) {
    try {
        // 检查是否是默认管理员
        const adminElement = document.querySelector(`[data-admin-id="${adminId}"]`);
        const isAdmin = adminElement && adminElement.closest('.device-item').querySelector('h3').textContent === 'admin';
        
        if (isAdmin) {
            utils.showNotification('不能删除默认管理员账户', 'error');
            return;
        }
        
        if (confirm('确定要删除这个管理员吗？')) {
            const response = await fetch(`/api/admins/${adminId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                utils.showNotification('管理员删除成功', 'success');
                this.loadAdmins(); // 重新加载管理员列表
            } else {
                const errorData = await response.json();
                utils.showNotification(`删除管理员失败: ${errorData.detail || '未知错误'}`, 'error');
            }
        }
    } catch (error) {
        utils.showNotification(`删除管理员时发生错误: ${error.message}`, 'error');
    }
};