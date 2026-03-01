/**
 * V3 前端组件加载器
 * 动态加载导航栏/侧边栏/面包屑组件
 * 
 * 使用方式:
 * <script src="js/components-loader.js"></script>
 * <script>
 *   loadComponents({
 *     title: '页面标题',
 *     breadcrumbs: ['首页', '当前页面']
 *   });
 * </script>
 */

(function() {
    'use strict';

    // 组件配置
    const COMPONENTS = {
        navbar: '../components/navbar.html',
        sidebar: '../components/sidebar.html',
        breadcrumb: '../components/breadcrumb.html'
    };

    // 全局状态
    const state = {
        isDark: false,
        isSidebarOpen: false,
        modules: [
            {id: 'hotnews', name: '热点中心', icon: '🔥', url: 'v3_hotnews_center_v2.html'},
            {id: 'topics', name: '智能选题', icon: '🎯', url: 'v3_topic_intelligence_v2.html'},
            {id: 'evaluation', name: '工作评价', icon: '📊', url: 'v3_evaluation_v2.html'},
            {id: 'review', name: '工作 Review', icon: '🔍', url: 'v3_work_review_v2.html'},
            {id: 'publish', name: '自动发布', icon: '📝', url: 'v3_publish_center_v2.html'},
            {id: 'dashboard', name: '数据看板', icon: '📈', url: 'v3_data_dashboard_v2.html'},
            {id: 'coordinator', name: '项目协调者', icon: '🤖', url: 'v3_coordinator_v2.html'},
            {id: 'workflow', name: '工作流引擎', icon: '🔗', url: 'v3_workflow_v2.html'},
            {id: 'writing', name: '写作工厂', icon: '✍️', url: 'v3_writing_factory_v2.html'},
            {id: 'user', name: '用户中心', icon: '👥', url: 'v3_user_center_v2.html'}
        ]
    };

    // 加载组件
    window.loadComponents = function(options = {}) {
        const { title = 'V3 页面', breadcrumbs = [] } = options;

        // 加载主题
        loadTheme();

        // 绑定快捷键
        bindShortcuts();

        // 更新页面标题
        document.title = title + ' - V3 统一门户';

        // 更新面包屑
        if (breadcrumbs.length > 0) {
            updateBreadcrumbs(breadcrumbs);
        }

        console.log('✅ 组件加载完成:', title);
    };

    // 加载主题
    function loadTheme() {
        const theme = localStorage.getItem('theme');
        state.isDark = theme === 'dark';
        if (state.isDark) {
            document.documentElement.classList.add('dark');
        }
    }

    // 绑定快捷键
    function bindShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + 1~9: 切换模块
            if (e.altKey && e.key >= '1' && e.key <= '9') {
                const index = parseInt(e.key) - 1;
                if (state.modules[index]) {
                    window.location.href = state.modules[index].url;
                }
            }
            // Alt + H: 返回首页
            if (e.altKey && e.key.toLowerCase() === 'h') {
                window.location.href = 'v3_portal_v2.html';
            }
            // Alt + S: 折叠侧边栏
            if (e.altKey && e.key.toLowerCase() === 's') {
                state.isSidebarOpen = !state.isSidebarOpen;
                document.querySelector('.sidebar')?.classList.toggle('hidden', !state.isSidebarOpen);
            }
            // Ctrl + K: 搜索
            if (e.ctrlKey && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                document.querySelector('input[type="search"]')?.focus();
            }
        });
    }

    // 更新面包屑
    function updateBreadcrumbs(breadcrumbs) {
        const breadcrumbEl = document.querySelector('.breadcrumb');
        if (!breadcrumbEl) return;

        breadcrumbEl.innerHTML = breadcrumbs.map((crumb, index) => {
            if (index === breadcrumbs.length - 1) {
                return `<span class="text-gray-900 font-medium">${crumb}</span>`;
            }
            return `<a href="#" class="hover:text-primary-500">${crumb}</a>`;
        }).join('<span class="mx-2">/</span>');
    }

    // 自动初始化
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🚀 V3 组件加载器已就绪');
    });
})();
