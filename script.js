class PomodoroApp {
    constructor() {
        this.elements = {
            timerText: document.getElementById('timer-text'),
            timerStatus: document.getElementById('timer-status'),
            startBtn: document.getElementById('start-btn'),
            pauseBtn: document.getElementById('pause-btn'),
            resumeBtn: document.getElementById('resume-btn'),
            resetBtn: document.getElementById('reset-btn'),
            completedCount: document.getElementById('completed-count'),
            focusTime: document.getElementById('focus-time'),
            errorMessage: document.getElementById('error-message'),
            errorText: document.getElementById('error-text'),
            errorClose: document.getElementById('error-close'),
            progressRing: document.querySelector('.progress-ring-progress'),
            container: document.querySelector('.timer-section')
        };
        
        this.progressCircumference = 2 * Math.PI * 90; // radius = 90
        this.pollingInterval = null;
        this.driftCorrection = {
            startTime: null,
            serverStartTime: null,
            lastSyncTime: null
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startPolling();
    }
    
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startTimer());
        this.elements.pauseBtn.addEventListener('click', () => this.pauseTimer());
        this.elements.resumeBtn.addEventListener('click', () => this.resumeTimer());
        this.elements.resetBtn.addEventListener('click', () => this.resetTimer());
        this.elements.errorClose.addEventListener('click', () => this.hideError());
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.updateTimerState(),
                this.updateTodayStats()
            ]);
        } catch (error) {
            this.showError('初期データの読み込みに失敗しました');
        }
    }
    
    startPolling() {
        // Poll every 100ms for smooth updates
        this.pollingInterval = setInterval(() => {
            this.updateTimerState();
        }, 100);
        
        // Update stats every 5 seconds
        setInterval(() => {
            this.updateTodayStats();
        }, 5000);
    }
    
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(endpoint, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
    
    async updateTimerState() {
        try {
            const state = await this.apiCall('/api/timer/state');
            this.displayTimerState(state);
        } catch (error) {
            this.showError('タイマー状態の取得に失敗しました');
        }
    }
    
    async updateTodayStats() {
        try {
            const stats = await this.apiCall('/api/stats/today');
            this.displayTodayStats(stats);
        } catch (error) {
            this.showError('統計データの取得に失敗しました');
        }
    }
    
    displayTimerState(state) {
        // Update timer display with drift correction
        let displayTime = state.time_display;
        
        if (state.state === 'running' && this.driftCorrection.serverStartTime) {
            displayTime = this.calculateDriftCorrectedTime(state);
        }
        
        this.elements.timerText.textContent = displayTime;
        
        // Update status
        const statusMap = {
            'stopped': '停止中',
            'running': '実行中',
            'paused': '一時停止中'
        };
        this.elements.timerStatus.textContent = statusMap[state.state] || '不明';
        
        // Update progress ring
        this.updateProgressRing(state.progress);
        
        // Update button states
        this.updateButtonStates(state.state);
        
        // Update visual state
        this.updateVisualState(state.state);
        
        // Update drift correction data
        if (state.state === 'running') {
            const now = Date.now();
            if (!this.driftCorrection.serverStartTime) {
                this.driftCorrection.serverStartTime = now - ((state.duration - state.remaining_time) * 1000);
                this.driftCorrection.startTime = now;
            }
            this.driftCorrection.lastSyncTime = now;
        } else {
            this.driftCorrection.serverStartTime = null;
            this.driftCorrection.startTime = null;
        }
    }
    
    calculateDriftCorrectedTime(state) {
        const now = Date.now();
        const elapsedMs = now - this.driftCorrection.serverStartTime;
        const elapsedSeconds = Math.floor(elapsedMs / 1000);
        const remainingSeconds = Math.max(0, state.duration - elapsedSeconds);
        
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    updateProgressRing(progress) {
        const offset = this.progressCircumference - (progress / 100) * this.progressCircumference;
        this.elements.progressRing.style.strokeDashoffset = offset;
    }
    
    updateButtonStates(state) {
        // Reset all button states
        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;
        this.elements.resumeBtn.style.display = 'none';
        this.elements.pauseBtn.style.display = 'inline-block';
        
        switch (state) {
            case 'stopped':
                this.elements.startBtn.disabled = false;
                break;
            case 'running':
                this.elements.startBtn.disabled = true;
                this.elements.pauseBtn.disabled = false;
                break;
            case 'paused':
                this.elements.startBtn.disabled = true;
                this.elements.pauseBtn.style.display = 'none';
                this.elements.resumeBtn.style.display = 'inline-block';
                this.elements.resumeBtn.disabled = false;
                break;
        }
    }
    
    updateVisualState(state) {
        // Remove all state classes
        this.elements.container.classList.remove('timer-running', 'timer-paused', 'timer-stopped');
        
        // Add current state class
        this.elements.container.classList.add(`timer-${state}`);
    }
    
    displayTodayStats(stats) {
        this.elements.completedCount.textContent = stats.completed_sessions;
        this.elements.focusTime.textContent = stats.focus_time_display;
    }
    
    async startTimer() {
        try {
            await this.apiCall('/api/timer/start', 'POST');
            this.driftCorrection.serverStartTime = null; // Reset for new start
            await this.updateTimerState();
        } catch (error) {
            this.showError('タイマーの開始に失敗しました');
        }
    }
    
    async pauseTimer() {
        try {
            await this.apiCall('/api/timer/pause', 'POST');
            this.driftCorrection.serverStartTime = null; // Clear drift correction
            await this.updateTimerState();
        } catch (error) {
            this.showError('タイマーの一時停止に失敗しました');
        }
    }
    
    async resumeTimer() {
        try {
            await this.apiCall('/api/timer/resume', 'POST');
            this.driftCorrection.serverStartTime = null; // Reset for resume
            await this.updateTimerState();
        } catch (error) {
            this.showError('タイマーの再開に失敗しました');
        }
    }
    
    async resetTimer() {
        try {
            await this.apiCall('/api/timer/reset', 'POST');
            this.driftCorrection.serverStartTime = null; // Clear drift correction
            await this.updateTimerState();
            await this.updateTodayStats(); // Refresh stats in case of completion
        } catch (error) {
            this.showError('タイマーのリセットに失敗しました');
        }
    }
    
    showError(message) {
        this.elements.errorText.textContent = message;
        this.elements.errorMessage.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }
    
    hideError() {
        this.elements.errorMessage.style.display = 'none';
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroApp();
});

// Handle visibility change to sync when tab becomes active
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Force update when tab becomes visible
        if (window.pomodoroApp) {
            window.pomodoroApp.updateTimerState();
            window.pomodoroApp.updateTodayStats();
        }
    }
});

// Store app instance globally for debugging
document.addEventListener('DOMContentLoaded', () => {
    window.pomodoroApp = new PomodoroApp();
});