// Form switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const signInForm = document.getElementById('signIn');
    const signUpForm = document.getElementById('signup');
    const recoverForm = document.getElementById('recoverPassword');
    
    const signUpButton = document.getElementById('signUpButton');
    const signInButton = document.getElementById('signInButton');
    const recoverPasswordLink = document.getElementById('recoverPasswordLink');
    const backToSignIn = document.getElementById('backToSignIn');
    
    // Password visibility toggles
    const togglePassword = document.getElementById('togglePassword');
    const toggleSignUpPassword = document.getElementById('toggleSignUpPassword');
    const passwordInput = document.getElementById('password');
    const signUpPasswordInput = document.getElementById('rPassword');
    
    // Form switching functions
    function showForm(targetForm) {
        [signInForm, signUpForm, recoverForm].forEach(form => {
            form.style.display = 'none';
            form.classList.remove('active');
        });
        
        targetForm.style.display = 'block';
        setTimeout(() => {
            targetForm.classList.add('active');
        }, 10);
        
        // Clear any existing messages
        document.querySelectorAll('.alert-message').forEach(msg => {
            msg.style.display = 'none';
        });
    }
    
    // Event listeners for form switching
    if (signUpButton) {
        signUpButton.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(signUpForm);
        });
    }
    
    if (signInButton) {
        signInButton.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(signInForm);
        });
    }
    
    if (recoverPasswordLink) {
        recoverPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(recoverForm);
        });
    }
    
    if (backToSignIn) {
        backToSignIn.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(signInForm);
        });
    }
    
    // Password visibility toggles
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = togglePassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    if (toggleSignUpPassword && signUpPasswordInput) {
        toggleSignUpPassword.addEventListener('click', () => {
            const type = signUpPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            signUpPasswordInput.setAttribute('type', type);
            
            const icon = toggleSignUpPassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    // Password strength checker
    if (signUpPasswordInput) {
        const strengthBars = document.querySelectorAll('.strength-bar');
        const strengthText = document.querySelector('.strength-text');
        const requirements = document.querySelectorAll('.requirement');
        
        signUpPasswordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            const strength = checkPasswordStrength(password);
            
            // Update strength bars
            strengthBars.forEach((bar, index) => {
                if (index < strength.score) {
                    bar.style.backgroundColor = getStrengthColor(strength.score);
                } else {
                    bar.style.backgroundColor = 'var(--gray-200)';
                }
            });
            
            // Update strength text
            if (strengthText) {
                strengthText.textContent = getStrengthLabel(strength.score);
            }
            
            // Update requirements
            requirements.forEach(req => {
                const reqType = req.getAttribute('data-requirement');
                if (strength.requirements[reqType]) {
                    req.classList.add('met');
                } else {
                    req.classList.remove('met');
                }
            });
        });
    }
    
    function checkPasswordStrength(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password)
        };
        
        const score = Object.values(requirements).filter(Boolean).length;
        
        return { requirements, score };
    }
    
    function getStrengthColor(score) {
        switch (score) {
            case 1: return 'var(--error-500)';
            case 2: return 'var(--warning-500)';
            case 3: return 'var(--warning-500)';
            case 4: return 'var(--success-500)';
            default: return 'var(--gray-200)';
        }
    }
    
    function getStrengthLabel(score) {
        switch (score) {
            case 0: return 'Password strength';
            case 1: return 'Very weak';
            case 2: return 'Weak';
            case 3: return 'Good';
            case 4: return 'Strong';
            default: return 'Password strength';
        }
    }
    
    // Form validation
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validateForm(formType) {
        if (formType === 'signIn') {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showMessage('Please fill in all fields.', 'signInMessage', 'warning');
                return false;
            }
            
            if (!validateEmail(email)) {
                showMessage('Please enter a valid email address.', 'signInMessage', 'error');
                return false;
            }
        }
        
        if (formType === 'signUp') {
            const email = document.getElementById('rEmail').value;
            const password = document.getElementById('rPassword').value;
            const firstName = document.getElementById('fName').value;
            const lastName = document.getElementById('lName').value;
            const agreeTerms = document.getElementById('agreeTerms').checked;
            
            if (!email || !password || !firstName || !lastName) {
                showMessage('Please fill in all required fields.', 'signUpMessage', 'warning');
                return false;
            }
            
            if (!validateEmail(email)) {
                showMessage('Please enter a valid email address.', 'signUpMessage', 'error');
                return false;
            }
            
            const strength = checkPasswordStrength(password);
            if (strength.score < 3) {
                showMessage('Please choose a stronger password.', 'signUpMessage', 'error');
                return false;
            }
            
            if (!agreeTerms) {
                showMessage('Please agree to the Terms of Service and Privacy Policy.', 'signUpMessage', 'warning');
                return false;
            }
        }
        
        return true;
    }
    
    // Enhanced message function
    window.showMessage = function(message, divId, type = 'error') {
        const messageDiv = document.getElementById(divId);
        messageDiv.className = `alert-message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        messageDiv.style.display = "flex";
        messageDiv.style.opacity = 1;
        
        setTimeout(() => {
            messageDiv.style.opacity = 0;
            setTimeout(() => {
                messageDiv.style.display = "none";
                messageDiv.style.opacity = 1;
            }, 300);
        }, 5000);
    };
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const activeForm = document.querySelector('.form-container.active');
            if (activeForm) {
                const submitButton = activeForm.querySelector('button[type="submit"], button[id^="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }
    });
    
    // Initialize with sign-in form
    showForm(signInForm);
});
