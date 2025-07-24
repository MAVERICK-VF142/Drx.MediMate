window.addEventListener('DOMContentLoaded', () => {
  const signInSection = document.getElementById('signIn');
  const signUpSection = document.getElementById('signup');
  const recoverSection = document.getElementById('recoverPassword');

  // Prevent link-based default behavior
  document.getElementById('signUpButton')?.addEventListener('click', (e) => {
    e.preventDefault();
    signInSection.style.display = 'none';
    signUpSection.style.display = 'block';
    recoverSection.style.display = 'none';
  });

  document.getElementById('signInButton')?.addEventListener('click', (e) => {
    e.preventDefault();
    signUpSection.style.display = 'none';
    signInSection.style.display = 'block';
    recoverSection.style.display = 'none';
  });

  document.getElementById('recoverPasswordLink')?.addEventListener('click', (e) => {
    e.preventDefault();
    signInSection.style.display = 'none';
    signUpSection.style.display = 'none';
    recoverSection.style.display = 'block';
  });

  document.getElementById('backToSignIn')?.addEventListener('click', (e) => {
    e.preventDefault();
    recoverSection.style.display = 'none';
    signInSection.style.display = 'block';
    signUpSection.style.display = 'none';
  });
});
