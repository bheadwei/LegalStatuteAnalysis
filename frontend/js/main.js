/**
 * 首頁邏輯 - 法條卡片展示
 */

let allLaws = [];  // 保存所有法條數據用於搜尋

/**
 * 頁面初始化
 */
document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    await loadLaws();
    setupSearchBox();
    setupBackToTop();
});

/**
 * 載入統計資訊
 */
async function loadStats() {
    const statsSection = document.getElementById('stats-section');

    try {
        UIUtils.showLoading(statsSection);
        const stats = await API.getStats();

        statsSection.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${UIUtils.formatNumber(stats.total_reports)}</div>
                <div class="stat-label">考卷總數</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${UIUtils.formatNumber(stats.total_questions)}</div>
                <div class="stat-label">題目總數</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${UIUtils.formatNumber(stats.total_laws)}</div>
                <div class="stat-label">涉及法條</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.years.length}</div>
                <div class="stat-label">考試年份</div>
            </div>
        `;
    } catch (error) {
        UIUtils.showError(statsSection, '無法載入統計資訊');
        console.error('載入統計資訊失敗:', error);
    }
}

/**
 * 載入法條列表
 */
async function loadLaws() {
    const lawsSection = document.getElementById('laws-section');

    try {
        UIUtils.showLoading(lawsSection);
        allLaws = await API.getAllLaws();
        renderLaws(allLaws);
    } catch (error) {
        UIUtils.showError(lawsSection, '無法載入法條列表');
        console.error('載入法條列表失敗:', error);
    }
}

/**
 * 渲染法條卡片
 */
function renderLaws(laws) {
    const lawsSection = document.getElementById('laws-section');

    if (laws.length === 0) {
        lawsSection.innerHTML = `
            <div class="card">
                <p style="text-align: center; color: var(--neutral-600);">
                    沒有找到符合的法條
                </p>
            </div>
        `;
        return;
    }

    const lawsHtml = laws.map(law => `
        <div class="law-card" onclick="viewLawDetail('${law.law_id}')">
            <div class="law-card-header">
                <div class="law-name">${law.law_name}</div>
                <div class="law-article">${law.article_no}</div>
            </div>
            <div class="law-card-body">
                <span class="law-category">${law.category}</span>
            </div>
            <div class="law-card-footer">
                <div class="match-count">
                    <span>匹配次數</span>
                    <span class="match-count-badge">${law.matched_count}</span>
                </div>
                <div style="color: var(--neutral-400); font-size: 1.25rem;">→</div>
            </div>
        </div>
    `).join('');

    lawsSection.innerHTML = `<div class="law-grid">${lawsHtml}</div>`;
}

/**
 * 設定搜尋框
 */
function setupSearchBox() {
    const searchBox = document.getElementById('search-box');

    searchBox.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();

        if (query === '') {
            renderLaws(allLaws);
            return;
        }

        const filteredLaws = allLaws.filter(law => {
            return (
                law.law_name.toLowerCase().includes(query) ||
                law.law_code.toLowerCase().includes(query) ||
                law.article_no.toLowerCase().includes(query) ||
                law.category.toLowerCase().includes(query)
            );
        });

        renderLaws(filteredLaws);
    });
}

/**
 * 查看法條詳細資料
 */
function viewLawDetail(lawId) {
    window.location.href = `/question.html?law_id=${encodeURIComponent(lawId)}`;
}

/**
 * 設定返回頂部按鈕
 */
function setupBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');

    // 滾動監聽
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'inline-flex';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // 點擊返回頂部
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}
