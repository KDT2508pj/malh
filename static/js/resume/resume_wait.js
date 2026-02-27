        // 진행률 시뮬레이션
        let progress = 0;
        const progressBar = document.getElementById('progressBar');
        const percentageText = document.getElementById('percentageText');

        // [Logic] 분석 프로세스 시뮬레이션
        function simulateAnalysis() {
            const interval = setInterval(() => {
                // 랜덤하게 증가 (1~5%)
                const increment = Math.floor(Math.random() * 5) + 1;
                progress += increment;

                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    
                    // 완료 처리
                    updateUI(progress);
                    
                    // 분석 완료 후 /resumes로 이동
                    setTimeout(() => {
                        alert("분석이 완료되었습니다.");
                        location.href = '/resumes';
                    }, 500); // 0.5초 딜레이 후 이동
                } else {
                    updateUI(progress);
                }
            }, 150); // 0.15초마다 업데이트
        }

        function updateUI(value) {
            progressBar.style.width = value + '%';
            percentageText.textContent = value + '%';
        }

        // 페이지 로드 시 시작
        window.onload = () => {
            // 에러 발생 시나리오 (주석 처리됨 - 실제 구현 시 try-catch 블록 내에서 처리)
            /*
            const hasError = false; 
            if (hasError) {
                // 최대 1회 재호출 로직 수행 후
                location.href = '/';
                return;
            }
            */
            
            simulateAnalysis();
        };