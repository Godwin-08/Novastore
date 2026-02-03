// Main JS - NovaStore

let currentCategory = 'tous'; // État global pour la catégorie

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. GESTION DU MENU PROFIL ---
    const profileTrigger = document.getElementById('profileTrigger');
    const profileMenu = document.getElementById('profileMenu');

    if (profileTrigger && profileMenu) {
        // Fermer si on clique ailleurs
        window.addEventListener('click', (e) => {
            if (profileMenu.classList.contains('show')) {
                if (!profileMenu.contains(e.target) && !profileTrigger.contains(e.target)) {
                    profileMenu.classList.remove('show');
                }
            }
        });

        // Ouvrir/Fermer au clic
        profileTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle('show');
        });
    }

    // --- 2. FILTRAGE PAR CATÉGORIE (BOUTIQUE) ---
    const filterLinks = document.querySelectorAll('.cat-link');
    filterLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const category = link.getAttribute('data-category');
            filtrerParCategorie(category, link);
        });
    });
    
    // --- 2b. FILTRAGE STOCK & PROMO ---
    const cbStock = document.getElementById('cbStock');
    const cbPromo = document.getElementById('cbPromo');
    
    if(cbStock) cbStock.addEventListener('change', applyFilters);
    if(cbPromo) cbPromo.addEventListener('change', applyFilters);

    // --- 2c. FILTRAGE PRIX & TRI ---
    const btnFilterPrice = document.getElementById('btnFilterPrice');
    const sortSelect = document.getElementById('sortSelect');
    if(btnFilterPrice) btnFilterPrice.addEventListener('click', applyFilters);
    if(sortSelect) sortSelect.addEventListener('change', applyFilters);

    // --- 3. MODAL PRODUIT ---
    const modal = document.getElementById('productModal');
    const modalClose = document.getElementById('modalCloseBtn');
    
    if(modalClose) modalClose.addEventListener('click', closeProductModal);
    if(modal) modal.addEventListener('click', (e) => { if(e.target === modal) closeProductModal(); });
    document.addEventListener('keydown', (e) => { if(e.key === 'Escape') closeProductModal(); });

    // --- 4. RECHERCHE ---
    const searchInput = document.getElementById('searchInput');
    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.card').forEach(card => {
                const name = card.querySelector('h3').innerText.toLowerCase();
                card.style.display = name.includes(term) ? 'block' : 'none';
            });
        });
    }

    // --- 5. ANIMATIONS AU SCROLL ---
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.reveal-on-scroll').forEach(el => scrollObserver.observe(el));
});

// --- FONCTIONS GLOBALES (Appelées depuis le HTML) ---

// Fonction pour ouvrir le modal produit
window.openProductModal = function({id='', nom='', prix='', image='', categorie='', description='', stock=0}) {
    const modal = document.getElementById('productModal');
    if(!modal) return;
    
    const img = document.getElementById('modalImg');
    const placeholder = document.getElementById('modalPlaceholder');
    
    // Reset Image
    if(img) { 
        img.style.display = 'block'; 
        img.src = image || ''; 
        img.onerror = function() {
            this.style.display = 'none';
            if(placeholder) placeholder.style.display = 'flex';
        };
    }
    if(placeholder) { placeholder.style.display = 'none'; }

    // Infos
    document.getElementById('modalName').innerText = nom || 'Produit';
    document.getElementById('modalCat').innerText = categorie || '';
    document.getElementById('modalDesc').innerText = description || '';
    document.getElementById('modalPrice').innerText = (prix ? prix + ' DH' : '—');
    
    // Stock & Bouton
    const stockEl = document.getElementById('modalStock');
    const addBtn = document.getElementById('modalAddBtn');
    const modalInfo = document.querySelector('.modal-info');
    
    // Reset bouton
    const newBtn = addBtn.cloneNode(true);
    addBtn.parentNode.replaceChild(newBtn, addBtn);

    // Reset alerte
    const existingForm = document.getElementById('stockAlertForm');
    if(existingForm) existingForm.remove();
    
    if (stock > 0) {
        stockEl.innerHTML = stock < 5 
            ? `<span style="color:#eab308">⚠️ Stock limité : ${stock} restants</span>` 
            : `<span style="color:#10b981">✅ En stock</span>`;
        newBtn.disabled = false;
        newBtn.style.background = '#1e293b';
        newBtn.style.cursor = 'pointer';
        newBtn.innerText = "🛒 Ajouter au panier";
        newBtn.onclick = () => window.ajouterAuPanier(id);
    } else {
        stockEl.innerHTML = `<span style="color:#ef4444">❌ Rupture de stock</span>`;
        newBtn.disabled = true;
        newBtn.style.background = '#cbd5e1';
        newBtn.style.cursor = 'not-allowed';
        newBtn.innerText = "Épuisé";
        
        // Formulaire alerte
        const formDiv = document.createElement('div');
        formDiv.id = 'stockAlertForm';
        formDiv.style.marginTop = '20px';
        formDiv.style.padding = '15px';
        formDiv.style.background = '#f8fafc';
        formDiv.style.borderRadius = '12px';
        formDiv.style.border = '1px solid #e2e8f0';
        formDiv.innerHTML = `
            <p style="font-size: 0.9rem; margin: 0 0 10px 0; color: #1e293b; font-weight: 600;">M'alerter du retour en stock :</p>
            <div style="display: flex; gap: 10px;">
                <input type="email" id="alertEmail" placeholder="votre@email.com" style="flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem;">
                <button onclick="window.subscribeStockAlert(, this)" style="background: #0f172a; color: white; border: none; padding: 0 20px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.2s;">OK</button>
            </div>`;
        modalInfo.appendChild(formDiv);
    }

    modal.classList.add('open');
    modal.setAttribute('aria-hidden','false');
};

// Fonction pour fermer le modal
window.closeProductModal = function(){
    const modal = document.getElementById('productModal');
    if(modal) {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden','true');
    }
};

// Fonction pour ajouter au panier
window.ajouterAuPanier = function(id) {
    fetch('/api/panier/ajouter', { 
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id: id}) 
    })
    .then(res => { if (!res.ok) return res.json().then(err => { throw new Error(err.error) }); return res.json(); })
    .then(data => {
        const count = document.getElementById('cart-count');
        if(count) { count.innerText = data.total; count.classList.add('bounce'); setTimeout(() => count.classList.remove('bounce'), 300); }
        showNotification("Produit ajouté au panier ! ✅");
    })
    .catch(err => showNotification("❌ " + err.message));
};

// Fonction pour s'inscrire à une alerte stock
window.subscribeStockAlert = function(id, btnElement) {
    const emailInput = document.getElementById('alertEmail');
    if(!emailInput || !emailInput.value || !emailInput.value.includes('@')) {
        showNotification("❌ Email invalide."); return;
    }
    const originalText = btnElement.innerText;
    btnElement.disabled = true; btnElement.innerText = "...";
    
    fetch('/api/alert/subscribe', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id: id, email: emailInput.value})
    })
    .then(res => res.json())
    .then(data => {
        showNotification("✅ " + data.message);
        const form = document.getElementById('stockAlertForm');
        if(form) form.innerHTML = `<div style="text-align: center; padding: 10px; color: #10b981; background: #ecfdf5; border-radius: 8px;"><strong>🔔 Alerte activée !</strong></div>`;
    })
    .catch(err => { showNotification("❌ Erreur."); btnElement.disabled = false; btnElement.innerText = originalText; });
};

// --- LOGIQUE DE FILTRAGE ET TRI ---
const groupesCategories = {
    'PC': ['pc'],
    'Vêtement': ['vêtement'],
    'Livre': ['livre'],
    'Téléphone': ['téléphone']
};

function filtrerParCategorie(cat, element) {
    currentCategory = cat;
    
    const sectionTitle = document.querySelector('.section-title');
    if (sectionTitle) sectionTitle.innerText = cat === 'tous' ? "Toute la boutique" : cat;
    
    document.querySelectorAll('.cat-link').forEach(l => l.classList.remove('active'));
    if(element) element.classList.add('active');
    
    applyFilters();
}

function applyFilters() {
    const grid = document.querySelector('.products-grid');
    if (!grid) return;

    // --- 1. Récupérer les valeurs de tous les filtres ---
    const cbStock = document.getElementById('cbStock');
    const cbPromo = document.getElementById('cbPromo');
    const priceMinInput = document.getElementById('priceMin');
    const priceMaxInput = document.getElementById('priceMax');
    const sortSelect = document.getElementById('sortSelect');
    
    const showInStockOnly = cbStock ? cbStock.checked : false;
    const showPromoOnly = cbPromo ? cbPromo.checked : false;
    const priceMin = parseFloat(priceMinInput.value) || 0;
    const priceMax = parseFloat(priceMaxInput.value) || Infinity;
    const sortBy = sortSelect ? sortSelect.value : 'pertinence';
    
    const subCategories = groupesCategories[currentCategory];
    
    // --- 2. Filtrer les produits ---
    const allProducts = Array.from(grid.children);
    let visibleProducts = [];

    allProducts.forEach(card => {
        if (!card.classList.contains('product-card')) return;

        const cardCat = card.getAttribute('data-category');
        const cardPromo = card.getAttribute('data-promo') === 'true';
        const cardStock = parseInt(card.getAttribute('data-stock') || '0');
        const cardPrice = parseFloat(card.getAttribute('data-price'));
        
        let isVisible = true;

        // Filtre Catégorie
        if (currentCategory.toLowerCase() !== 'tous') {
            if (!subCategories || !cardCat || !subCategories.includes(cardCat.toLowerCase())) isVisible = false;
        }
        
        // Filtre Stock
        if (showInStockOnly && cardStock <= 0) isVisible = false;
        
        // Filtre Promo
        if (showPromoOnly && !cardPromo) isVisible = false;
        
        // Filtre Prix
        if (cardPrice < priceMin || cardPrice > priceMax) isVisible = false;

        if (isVisible) visibleProducts.push(card);
    });

    // --- 3. Trier les produits visibles ---
    visibleProducts.sort((a, b) => {
        switch (sortBy) {
            case 'prix-asc': return parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price'));
            case 'prix-desc': return parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price'));
            case 'nom-asc': return a.querySelector('h3').innerText.localeCompare(b.querySelector('h3').innerText);
            default: return parseInt(a.getAttribute('data-id')) - parseInt(b.getAttribute('data-id'));
        }
    });

    // --- 4. Mettre à jour l'affichage ---
    allProducts.forEach(card => card.style.display = 'none');
    visibleProducts.forEach(card => {
        grid.appendChild(card); // Ré-insère dans le bon ordre
        card.style.display = 'block';
    });
}

// Fonction pour afficher les notifications
function showNotification(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerText = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
}
