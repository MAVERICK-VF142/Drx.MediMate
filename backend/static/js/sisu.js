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