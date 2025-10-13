/**
 * API 呼叫封裝
 * 提供所有後端 API 的前端呼叫介面
 */

const API_BASE_URL = window.location.origin;

/**
 * API 工具類
 */
class API {
    /**
     * 通用 GET 請求
     */
    static async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API GET Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * 獲取統計資訊
     */
    static async getStats() {
        return await this.get('/api/stats');
    }

    /**
     * 獲取所有報告列表
     */
    static async getAllReports() {
        return await this.get('/api/reports');
    }

    /**
     * 獲取特定報告詳細資料
     * @param {string} reportId - 報告 ID
     */
    static async getReportDetail(reportId) {
        return await this.get(`/api/report/${reportId}`);
    }

    /**
     * 獲取所有法條列表（按匹配次數排序）
     */
    static async getAllLaws() {
        return await this.get('/api/laws');
    }

    /**
     * 獲取特定法條的詳細資料和相關題目
     * @param {string} lawId - 法條 ID
     */
    static async getLawDetail(lawId) {
        return await this.get(`/api/law/${lawId}`);
    }

    /**
     * 健康檢查
     */
    static async healthCheck() {
        return await this.get('/api/health');
    }
}

/**
 * UI 工具函數
 */
class UIUtils {
    /**
     * 顯示載入動畫
     */
    static showLoading(container) {
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
    }

    /**
     * 顯示錯誤訊息
     */
    static showError(container, message) {
        container.innerHTML = `
            <div class="card" style="background: #fee2e2; border-color: #fecaca;">
                <p style="color: #b91c1c; font-weight: 500;">❌ ${message}</p>
            </div>
        `;
    }

    /**
     * 格式化數字（加千分位）
     */
    static formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * 格式化百分比
     */
    static formatPercentage(num) {
        return `${(num * 100).toFixed(1)}%`;
    }

    /**
     * 取得 URL 參數
     */
    static getUrlParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    /**
     * 設定 URL 參數（不重新載入頁面）
     */
    static setUrlParam(param, value) {
        const url = new URL(window.location);
        url.searchParams.set(param, value);
        window.history.pushState({}, '', url);
    }

    /**
     * 平滑滾動到元素
     */
    static scrollToElement(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 導出到全域
window.API = API;
window.UIUtils = UIUtils;
