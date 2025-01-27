
// Modal oyna funksiyasi
document.addEventListener('DOMContentLoaded', () => {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const closeButtons = document.querySelectorAll('[data-close-button]');
    const overlay = document.getElementById('overlay');

    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modal = document.querySelector(trigger.dataset.modalTarget);
            openModal(modal);
        });
    });

    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    overlay.addEventListener('click', () => {
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => closeModal(modal));
    });

    function openModal(modal) {
        if (modal == null) return;
        modal.classList.add('active');
        overlay.classList.add('active');
    }

    function closeModal(modal) {
        if (modal == null) return;
        modal.classList.remove('active');
        overlay.classList.remove('active');
    }
});

// Formni tekshirish
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (event) => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });

        if (!isValid) {
            event.preventDefault();
            alert('すべての項目を記入してください！');
        }
    });
});

// Qidiruv maydoni uchun dinamik filtr
const searchInput = document.getElementById('search_date');
if (searchInput) {
    searchInput.addEventListener('input', () => {
        const filter = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const date = row.querySelector('td').textContent.toLowerCase();
            if (date.includes(filter)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}




// Hover animatsiya
const navLinks = document.querySelectorAll('nav a');
navLinks.forEach(link => {
    link.addEventListener('mouseover', () => {
        link.style.transform = 'scale(1.1)';
        link.style.transition = 'transform 0.3s ease-in-out';
    });

    link.addEventListener('mouseout', () => {
        link.style.transform = 'scale(1)';
    });
});

// Qo‘shish tugmasi uchun animatsiya
const buttons = document.querySelectorAll('button');
buttons.forEach(button => {
    button.addEventListener('click', () => {
        button.classList.add('clicked');
        setTimeout(() => button.classList.remove('clicked'), 200);
    });
});

    document.querySelector("form").addEventListener("submit", function (event) {
        const password = document.getElementById("password").value;
        if (password.length < 8) {
            event.preventDefault(); // Formani yuborishni to‘xtatadi
            alert("パスワードは8文字以上である必要があります！");
        }
    });


