// API基础URL
const API_BASE_URL = '';

// DOM元素
const profileForm = document.getElementById('profile-form');
const saveProfileBtn = document.getElementById('save-profile-btn');
const skipBtn = document.getElementById('skip-btn');
const profileStatus = document.getElementById('profile-status');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否已有用户信息
    checkAndLoadUserProfile();
    
    // 绑定表单提交事件
    profileForm.addEventListener('submit', handleProfileSubmit);
    
    // 绑定跳过按钮事件
    skipBtn.addEventListener('click', handleSkip);
});

// 检查并加载用户信息
async function checkAndLoadUserProfile() {
    const userId = getUserId();
    
    if (userId) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`);
            if (response.ok) {
                const userData = await response.json();
                
                // 先填充现有信息
                fillProfileForm(userData.profile);
                
                // 如果用户信息完整，询问是否直接进入简历维护
                if (userData.profile && userData.profile.name && userData.profile.email) {
                    if (confirm(`欢迎回来，${userData.profile.name}！是否直接进入简历维护页面？`)) {
                        window.location.href = '/static/index.html';
                        return;
                    }
                }
            } else {
                // 处理HTTP错误响应
                const errorData = await response.json().catch(() => ({ detail: '未知错误' }));
                console.error(`获取用户信息失败: ${response.status}: ${errorData.detail}`);
                
                // 如果是404错误（用户不存在），这是正常情况，不需要显示错误
                if (response.status !== 404) {
                    showMessage(`获取用户信息失败: ${errorData.detail}`, 'error');
                }
            }
        } catch (error) {
            console.error('检查用户信息失败:', error);
            showMessage('网络错误，请检查网络连接', 'error');
        }
    }
}



// 填充表单数据
function fillProfileForm(profile) {
    if (!profile) return;
    
    document.getElementById('user-name').value = profile.name || '';
    document.getElementById('user-email').value = profile.email || '';
    document.getElementById('user-phone').value = profile.phone || '';
    document.getElementById('user-gender').value = profile.gender || '未指定';
    document.getElementById('user-birth').value = profile.birth_date || '';
    document.getElementById('user-address').value = profile.address || '';
    document.getElementById('user-education').value = profile.education_level || '';
    document.getElementById('user-experience').value = profile.work_experience || '';
    document.getElementById('user-skills').value = profile.skills ? profile.skills.join(', ') : '';
    document.getElementById('user-summary').value = profile.summary || '';
}

// 处理表单提交
async function handleProfileSubmit(event) {
    event.preventDefault();
    
    const formData = getFormData();
    
    // 验证必填字段
    if (!formData.name || !formData.email || !formData.phone) {
        showMessage('请填写所有必填字段', 'error');
        return;
    }
    
    // 验证邮箱格式
    if (!isValidEmail(formData.email)) {
        showMessage('请输入有效的邮箱地址', 'error');
        return;
    }
    
    try {
        saveProfileBtn.disabled = true;
        saveProfileBtn.textContent = '保存中...';
        
        const userId = getUserId() || generateUserId();
        const profileData = {
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            gender: formData.gender,
            address: formData.address
        };
        
        let response;
        if (getUserId()) {
            // 更新用户信息
            response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
        } else {
            // 创建新用户
            response = await fetch(`${API_BASE_URL}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
        }
        
        if (response.ok) {
            const result = await response.json();
            setUserId(result.user_id || userId);
            showMessage('用户信息保存成功！', 'success');
            
            // 延迟跳转到简历维护页面
            setTimeout(() => {
                window.location.href = '/static/index.html';
            }, 1500);
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存失败，请重试', 'error');
        }
    } catch (error) {
        console.error('保存用户信息失败:', error);
        showMessage('网络错误，请检查网络连接', 'error');
    } finally {
        saveProfileBtn.disabled = false;
        saveProfileBtn.textContent = '保存信息';
    }
}

// 处理跳过按钮
function handleSkip() {
    if (confirm('跳过基本信息维护可能会影响简历生成效果，确定要跳过吗？')) {
        // 生成临时用户ID
        if (!getUserId()) {
            setUserId(generateUserId());
        }
        window.location.href = '/static/index.html';
    }
}

// 获取表单数据
function getFormData() {
    return {
        name: document.getElementById('user-name').value.trim(),
        email: document.getElementById('user-email').value.trim(),
        phone: document.getElementById('user-phone').value.trim(),
        gender: document.getElementById('user-gender').value,
        birth_date: document.getElementById('user-birth').value,
        address: document.getElementById('user-address').value.trim(),
        education_level: document.getElementById('user-education').value,
        work_experience: document.getElementById('user-experience').value,
        skills: document.getElementById('user-skills').value.trim(),
        summary: document.getElementById('user-summary').value.trim()
    };
}

// 验证邮箱格式
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 获取用户ID
function getUserId() {
    let userId = localStorage.getItem('resumeai_user_id');
    
    // 检查是否是旧格式的用户ID（以user_开头）
    if (userId && userId.startsWith('user_')) {
        // 清除旧格式的用户ID
        localStorage.removeItem('resumeai_user_id');
        userId = null;
    }
    
    // 如果没有用户ID或者是旧格式，生成新的UUID格式用户ID
    if (!userId) {
        userId = generateUserId();
        setUserId(userId);
    }
    
    return userId;
}

// 设置用户ID
function setUserId(userId) {
    localStorage.setItem('resumeai_user_id', userId);
}

// 生成用户ID (UUID格式)
function generateUserId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 显示消息
function showMessage(message, type) {
    profileStatus.innerHTML = `<div class="message ${type}">${message}</div>`;
    
    // 3秒后自动清除消息
    setTimeout(() => {
        profileStatus.innerHTML = '';
    }, 3000);
}