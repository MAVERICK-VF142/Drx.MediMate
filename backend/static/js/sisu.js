        // Switch between forms
        document.getElementById('signUpButton').addEventListener('click', () => {
            document.getElementById('signIn').style.display = 'none';
            document.getElementById('signup').style.display = 'block';
        });

        document.getElementById('signInButton').addEventListener('click', () => {
            document.getElementById('signup').style.display = 'none';
            document.getElementById('signIn').style.display = 'block';
        });

        document.getElementById('recoverPasswordLink').addEventListener('click', () => {
            document.getElementById('signIn').style.display = 'none';
            document.getElementById('recoverPassword').style.display = 'block';
        });

        document.getElementById('backToSignIn').addEventListener('click', () => {
            document.getElementById('recoverPassword').style.display = 'none';
            document.getElementById('signIn').style.display = 'block';
        });

        document.getElementById('signInForm').addEventListener('submit', function (e) {
            const emailInput = document.getElementById('email');
            const emailError = document.getElementById('emailError');

            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$/;


            if (!emailPattern.test(emailInput.value.trim())) {
                e.preventDefault();
                emailError.textContent = "Please enter a valid email address.";
                emailError.style.display = "block";
            } else {
                emailError.style.display = "none";
            }
        });