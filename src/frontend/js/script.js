

// Utility Functions
function showDialog(dialogId) {
    const dialog = document.getElementById(dialogId);
    dialog.style.display = 'flex';
    dialog.classList.add('active');
}

function hideDialog(dialogId) {
    const dialog = document.getElementById(dialogId);
    dialog.style.display = 'none';
    dialog.classList.remove('active');
}

function split2(s) {
    // Always return two non-empty strings to preserve line height
    if (s && s.includes('/')) {
        let [left, right] = s.split('/', 2);
        left = left.trim() || '\u00A0';
        right = right.trim() || '\u00A0';
        return [left, right];
    }
    const val = s ? s.trim() : '';
    if (val) {
        // Single value: display on first line, blank second line
        return [val, '\u00A0'];
    }
    // Both blank
    return ['\u00A0', '\u00A0'];
}

function join2(a, b) {
    a = a ? a.trim() : '';
    b = b ? b.trim() : '';
    if (a && b) {
        return `${a}/${b}`;
    } else if (a) {
        return a;
    } else if (b) {
        return b;
    }
    return '';
}

function formatCurrency(amount) {
    if (typeof amount !== 'number') {
        amount = parseFloat(amount);
    }
    if (isNaN(amount)) {
        return '';
    }
    return amount.toLocaleString('ko-KR') + ' 원';
}

// API Interaction Functions
async function fetchData(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Error: ' + error.message);
        return null;
    }
}

async function fetchProducts(filters = {}) {
    const params = new URLSearchParams();
    for (const key in filters) {
        if (filters[key]) {
            params.append(key, filters[key]);
        }
    }
    return fetchData(`/api/products/?${params.toString()}`);
}

async function fetchSalesRecords(filters = {}) {
    const params = new URLSearchParams();
    for (const key in filters) {
        if (filters[key]) {
            params.append(key, filters[key]);
        }
    }
    return fetchData(`/api/sales/?${params.toString()}`);
}

async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await fetch('/api/upload_image/', {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Image upload error:', error);
        alert('Error uploading image: ' + error.message);
        return null;
    }
}

// UI Rendering Functions
function displayProducts(products) {
    const imageList = document.getElementById('image-list');
    const productTableBody = document.querySelector('#product-table tbody');
    imageList.innerHTML = '';
    productTableBody.innerHTML = '';

    const categoryMap = {"E": "귀걸이", "R": "반지", "N": "목걸이", "B": "팔찌", "O": "기타"};

    products.forEach(p => {
        // Image Tab
        const imageItem = document.createElement('div');
        imageItem.className = 'image-item';
        imageItem.dataset.productId = p.id;
        imageItem.innerHTML = `
            <img src="${p.image_path ? '/images/' + p.image_path.split('/').pop() : ''}" alt="${p.name}">
            <p>${p.is_favorite ? '★ ' : ''}${p.name}</p>
            <p>${p.karat} ${p.weight_g}g</p>
        `;
        imageItem.addEventListener('dblclick', () => showProductDetail(p.id));
        imageList.appendChild(imageItem);

        // List Tab
        const row = productTableBody.insertRow();
        row.dataset.productId = p.id;
        row.addEventListener('dblclick', () => showProductDetail(p.id));

        const categoryKor = categoryMap[p.category] || p.category;
        const [basicLeft, basicRight] = split2(p.basic_extra);
        const [bulimLeft, bulimRight] = split2(p.mid_back_bulim);
        const [laborLeft, laborRight] = split2(p.mid_back_labor);

        row.innerHTML = `
            <td>${p.id}</td>
            <td><img src="${p.image_path ? '/images/' + p.image_path.split('/').pop() : ''}" alt="${p.name}"></td>
            <td>${categoryKor}</td>
            <td>${p.supplier_name}</td>
            <td>${p.supplier_item_no}</td>
            <td>${p.name}</td>
            <td>${p.product_code}</td>
            <td>${p.karat}</td>
            <td>${p.weight_g}</td>
            <td>${p.size}</td>
            <td>${p.total_qb_qty}</td>
            <td>
              <div>${basicLeft}</div>
              <div>${basicRight}</div>
            </td>
            <td>
              <div>${bulimLeft}</div>
              <div>${bulimRight}</div>
            </td>
            <td>
              <div>${laborLeft}</div>
              <div>${laborRight}</div>
            </td>
            <td>${p.cubic_labor}</td>
            <td>${p.total_labor}</td>
            <td>${p.discontinued ? 'Y' : 'N'}</td>
            <td>${p.stock_qty}</td>
            <td><button class="fav-btn" data-id="${p.id}">${p.is_favorite ? '★' : '☆'}</button></td>
            <td><button class="edit-btn" data-id="${p.id}">✎</button></td>
        `;

        // "수정" 버튼이 항상 폼을 열게 함, robust event binding
        const editBtn = row.querySelector('.edit-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showProductForm(p.id);
            });
        }

        // "즐겨찾기" 버튼 이벤트
        const favBtn = row.querySelector('.fav-btn');
        if (favBtn) {
            favBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleFavorite(p.id);
            });
        }

        // Row selection (excluding button clicks)
        row.addEventListener('click', (e) => {
            // 버튼을 클릭했을 때는 row 선택 동작 무시
            if (
                e.target.classList.contains('edit-btn') ||
                e.target.classList.contains('fav-btn')
            ) return;
            document.querySelectorAll('#product-table tbody tr').forEach(r => r.classList.remove('selected'));
            row.classList.add('selected');
        });
    });
}

function displaySalesRecords(salesRecords) {
    const salesTableBody = document.querySelector('#sales-table tbody');
    salesTableBody.innerHTML = '';

    salesRecords.forEach(record => {
        const row = salesTableBody.insertRow();
        row.dataset.salesId = record.id;
        row.addEventListener('dblclick', () => showSalesRecordDetail(record.id));

        row.innerHTML = `
            <td>${record.sale_date}</td>
            <td>${record.customer_name}</td>
            <td>${record.product_name}</td>
            <td>${formatCurrency(record.final_sale_price)}</td>
            <td><button class="edit-btn" data-id="${record.id}">✎</button></td>
        `;
        // "수정" 버튼이 폼을 열게 함
        const editBtn = row.querySelector('.edit-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showSalesRecordForm(record.id);
            });
        }
        // 클릭 시 선택 표시를 주어 삭제 대상을 지정할 수 있게 함
        row.addEventListener('click', () => {
            document.querySelectorAll('#sales-table tbody tr').forEach(r => r.classList.remove('selected'));
            row.classList.add('selected');
        });
    });
}

// Dialog Specific Functions
async function showProductDetail(productId) {
    const product = await fetchData(`/api/products/${productId}`);
    if (!product) return;

    document.getElementById('detail-main-image').src = product.image_path ? '/images/' + product.image_path.split('/').pop() : '';
    document.getElementById('detail-category').textContent = product.category;
    document.getElementById('detail-supplier-name').textContent = product.supplier_name;
    document.getElementById('detail-supplier-item-no').textContent = product.supplier_item_no;
    document.getElementById('detail-name').textContent = product.name;
    document.getElementById('detail-product-code').textContent = product.product_code;
    document.getElementById('detail-karat').textContent = product.karat;
    document.getElementById('detail-weight').textContent = `${product.weight_g} g`;
    document.getElementById('detail-size').textContent = product.size;
    document.getElementById('detail-total-qb-qty').textContent = product.total_qb_qty;
    const [basicLeft, basicRight] = split2(product.basic_extra);
    document.getElementById('detail-basic-extra').textContent = `${basicLeft} / ${basicRight}`;
    const [bulimLeft, bulimRight] = split2(product.mid_back_bulim);
    document.getElementById('detail-mid-back-bulim').textContent = `${bulimLeft} / ${bulimRight}`;
    const [laborLeft, laborRight] = split2(product.mid_back_labor);
    document.getElementById('detail-mid-back-labor').textContent = `${laborLeft} / ${laborRight}`;
    document.getElementById('detail-cubic-labor').textContent = product.cubic_labor;
    document.getElementById('detail-total-labor').textContent = product.total_labor;
    document.getElementById('detail-notes').textContent = product.notes || '-';

    // Handle extra images (if any)
    const extraImagesContainer = document.getElementById('detail-extra-images');
    extraImagesContainer.innerHTML = '';
    if (product.extra_images && product.extra_images.length > 0) {
        product.extra_images.forEach(imgPath => {
            const img = document.createElement('img');
            img.src = '/images/' + imgPath.split('/').pop();
            extraImagesContainer.appendChild(img);
        });
    }

    // Set up sell button
    const detailSellBtn = document.getElementById('detail-sell-btn');
    detailSellBtn.onclick = () => {
        hideDialog('product-detail-dialog');
        showSalesRecordForm(null, product); // Pass product to pre-fill sales record
    };

    showDialog('product-detail-dialog');
}

async function showProductForm(productId = null) {
    const formTitle = document.getElementById('product-form-title');
    const productForm = document.getElementById('product-form');
    productForm.reset(); // Clear previous data
    productForm.dataset.productId = productId; // Store product ID for update

    // Clear image input value
    document.getElementById('image-upload-input').value = '';

    // Show dialog immediately
    showDialog('product-form-dialog');

    if (productId) {
        formTitle.textContent = '상품 정보 수정';
        const product = await fetchData(`/api/products/${productId}`);
        if (!product) return;
        document.getElementById('form-category').value = product.category;
        document.getElementById('form-supplier-name').value = product.supplier_name;
        document.getElementById('form-supplier-item-no').value = product.supplier_item_no;
        document.getElementById('form-product-code').value = product.product_code;
        document.getElementById('form-name').value = product.name;
        document.getElementById('form-karat').value = product.karat;
        document.getElementById('form-weight-g').value = product.weight_g;
        document.getElementById('form-size').value = product.size;
        document.getElementById('form-total-qb-qty').value = product.total_qb_qty;

        const [basicLeft, basicRight] = split2(product.basic_extra);
        document.getElementById('form-basic-extra-left').value = basicLeft;
        document.getElementById('form-basic-extra-right').value = basicRight;

        const [bulimLeft, bulimRight] = split2(product.mid_back_bulim);
        document.getElementById('form-mid-back-bulim-left').value = bulimLeft;
        document.getElementById('form-mid-back-bulim-right').value = bulimRight;

        const [laborLeft, laborRight] = split2(product.mid_back_labor);
        document.getElementById('form-mid-back-labor-left').value = laborLeft;
        document.getElementById('form-mid-back-labor-right').value = laborRight;

        document.getElementById('form-cubic-labor').value = product.cubic_labor;
        document.getElementById('form-total-labor').value = product.total_labor;
        document.getElementById('form-discontinued').value = product.discontinued ? 'Y' : 'N';
        document.getElementById('form-stock-qty').value = product.stock_qty;
        document.getElementById('form-image-path').value = product.image_path;
        document.getElementById('form-is-favorite').checked = product.is_favorite;
        document.getElementById('form-notes').value = product.notes;
    } else {
        formTitle.textContent = '새 상품 등록';
    }
}

async function showSalesRecordForm(salesId = null, product = null) {
    const formTitle = document.getElementById('sales-record-form-title');
    const salesRecordForm = document.getElementById('sales-record-form');
    salesRecordForm.reset();
    salesRecordForm.dataset.salesId = salesId;

    // Set current date for new records
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('sr-sale-date').value = today;

    if (salesId) {
        formTitle.textContent = '판매 기록 수정';
        const record = await fetchData(`/api/sales/${salesId}`);
        if (!record) return;
        document.getElementById('sr-sale-date').value = record.sale_date;
        document.getElementById('sr-customer-name').value = record.customer_name;
        document.getElementById('sr-sale-type').value = record.sale_type;
        document.getElementById('sr-return-reason').value = record.return_reason;
        document.getElementById('sr-purchase-market-price').value = record.purchase_market_price;
        document.getElementById('sr-sale-market-price').value = record.sale_market_price;
        document.getElementById('sr-final-sale-price').value = record.final_sale_price;
        document.getElementById('sr-product-supplier').value = record.product_spplier;
        document.getElementById('sr-product-name').value = record.product_name;
        document.getElementById('sr-karat-unit').value = record.karat_unit;
        document.getElementById('sr-karat-g').value = record.karat_g;
        document.getElementById('sr-quantity').value = record.quantity;
        document.getElementById('sr-color').value = record.color;
        document.getElementById('sr-size').value = record.size;
        document.getElementById('sr-main-stone-type').value = record.main_stone_type;
        document.getElementById('sr-main-stone-quantity').value = record.main_stone_quantity;
        document.getElementById('sr-main-stone-purchase-price').value = record.main_stone_purchase_price;
        document.getElementById('sr-main-stone-sale-price').value = record.main_stone_sale_price;
        document.getElementById('sr-aux-stone-type').value = record.aux_stone_type;
        document.getElementById('sr-aux-stone-quantity').value = record.aux_stone_quantity;
        document.getElementById('sr-aux-stone-purchase-price').value = record.aux_stone_purchase_price;
        document.getElementById('sr-aux-stone-sale-price').value = record.aux_stone_sale_price;
        document.getElementById('sr-notes').value = record.notes;

        const [basicLeft, basicRight] = split2(record.basic_extra);
        document.getElementById('sr-basic-extra-left').value = basicLeft;
        document.getElementById('sr-basic-extra-right').value = basicRight;

        const [bulimLeft, bulimRight] = split2(record.mid_back_bulim);
        document.getElementById('sr-mid-back-bulim-left').value = bulimLeft;
        document.getElementById('sr-mid-back-bulim-right').value = bulimRight;

    } else {
        formTitle.textContent = '판매 기록 등록';
        if (product) {
            document.getElementById('sr-product-supplier').value = product.supplier_name;
            document.getElementById('sr-product-name').value = product.name;
            const [basicLeft, basicRight] = split2(product.basic_extra);
            document.getElementById('sr-basic-extra-left').value = basicLeft;
            document.getElementById('sr-basic-extra-right').value = basicRight;
            const [bulimLeft, bulimRight] = split2(product.mid_back_bulim);
            document.getElementById('sr-mid-back-bulim-left').value = bulimLeft;
            document.getElementById('sr-mid-back-bulim-right').value = bulimRight;
        }
    }
    showDialog('sales-record-dialog');
}

async function showSalesRecordDetail(salesId) {
    const record = await fetchData(`/api/sales/${salesId}`);
    if (!record) return;

    document.getElementById('srd-sale-date').textContent = record.sale_date;
    document.getElementById('srd-customer-name').textContent = record.customer_name;
    document.getElementById('srd-sale-type').textContent = record.sale_type;
    document.getElementById('srd-return-reason').textContent = record.return_reason || '-';
    document.getElementById('srd-product-supplier').textContent = record.product_spplier;
    document.getElementById('srd-product-name').textContent = record.product_name;
    document.getElementById('srd-purchase-market-price').textContent = formatCurrency(record.purchase_market_price);
    document.getElementById('srd-sale-market-price').textContent = formatCurrency(record.sale_market_price);
    document.getElementById('srd-final-sale-price').textContent = formatCurrency(record.final_sale_price);
    const [sBasicLeft, sBasicRight] = split2(record.basic_extra);
    document.getElementById('srd-basic-extra').textContent = `${sBasicLeft} / ${sBasicRight}`;
    const [sBulimLeft, sBulimRight] = split2(record.mid_back_bulim);
    document.getElementById('srd-mid-back-bulim').textContent = `${sBulimLeft} / ${sBulimRight}`;
    document.getElementById('srd-quantity').textContent = record.quantity;
    document.getElementById('srd-color').textContent = record.color;
    document.getElementById('srd-size').textContent = record.size;
    document.getElementById('srd-main-stone-type').textContent = record.main_stone_type;
    document.getElementById('srd-main-stone-quantity').textContent = record.main_stone_quantity;
    document.getElementById('srd-main-stone-purchase-price').textContent = formatCurrency(record.main_stone_purchase_price);
    document.getElementById('srd-main-stone-sale-price').textContent = formatCurrency(record.main_stone_sale_price);
    document.getElementById('srd-aux-stone-type').textContent = record.aux_stone_type;
    document.getElementById('srd-aux-stone-quantity').textContent = record.aux_stone_quantity;
    document.getElementById('srd-aux-stone-purchase-price').textContent = formatCurrency(record.aux_stone_purchase_price);
    document.getElementById('srd-aux-stone-sale-price').textContent = formatCurrency(record.aux_stone_sale_price);
    document.getElementById('srd-notes').textContent = record.notes || '-';

    showDialog('sales-record-detail-dialog');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            document.getElementById(`${button.dataset.tab}-tab`).classList.add('active');
            if (button.dataset.tab === 'sales') {
                loadSales();
            } else {
                loadProducts();
            }
        });
    });

    // Product Search & Reset
    document.getElementById('search-btn-img').addEventListener('click', () => {
        const filters = {
            category: document.getElementById('category-img').value,
            supplier_name: document.getElementById('supplier-name-img').value,
            supplier_item_no: document.getElementById('supplier-item-no-img').value,
            name: document.getElementById('name-img').value,
            product_code: document.getElementById('product-code-img').value,
            discontinued: document.getElementById('discontinued-img').value === 'Y' ? true : (document.getElementById('discontinued-img').value === 'N' ? false : null),
        };
        loadProducts(filters);
    });
    document.getElementById('reset-btn-img').addEventListener('click', () => {
        document.getElementById('category-img').value = '';
        document.getElementById('supplier-name-img').value = '';
        document.getElementById('supplier-item-no-img').value = '';
        document.getElementById('name-img').value = '';
        document.getElementById('product-code-img').value = '';
        document.getElementById('discontinued-img').value = '';
        loadProducts();
    });

    document.getElementById('search-btn-list').addEventListener('click', () => {
        const filters = {
            category: document.getElementById('category-list').value,
            supplier_name: document.getElementById('supplier-name-list').value,
            supplier_item_no: document.getElementById('supplier-item-no-list').value,
            name: document.getElementById('name-list').value,
            product_code: document.getElementById('product-code-list').value,
            discontinued: document.getElementById('discontinued-list').value === 'Y' ? true : (document.getElementById('discontinued-list').value === 'N' ? false : null),
        };
        loadProducts(filters);
    });
    document.getElementById('reset-btn-list').addEventListener('click', () => {
        document.getElementById('category-list').value = '';
        document.getElementById('supplier-name-list').value = '';
        document.getElementById('supplier-item-no-list').value = '';
        document.getElementById('name-list').value = '';
        document.getElementById('product-code-list').value = '';
        document.getElementById('discontinued-list').value = '';
        loadProducts();
    });

    // Sales Search & Reset
    document.getElementById('sales-search-btn').addEventListener('click', () => {
        const filters = {
            start_date: document.getElementById('sales-start-date').value,
            end_date: document.getElementById('sales-end-date').value,
            customer_name: document.getElementById('sales-customer-name').value,
            product_name: document.getElementById('sales-product-name').value,
        };
        loadSales(filters);
    });
    document.getElementById('sales-reset-btn').addEventListener('click', () => {
        const today = new Date();
        const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
        document.getElementById('sales-start-date').value = oneMonthAgo.toISOString().split('T')[0];
        document.getElementById('sales-end-date').value = today.toISOString().split('T')[0];
        document.getElementById('sales-customer-name').value = '';
        document.getElementById('sales-product-name').value = '';
        loadSales();
    });

    // Action Buttons (contextual for Product vs Sales)
    document.getElementById('add-btn').addEventListener('click', () => {
        const currentTab = document.querySelector('.tab-button.active').dataset.tab;
        if (currentTab === 'sales') {
            showSalesRecordForm();
        } else {
            showProductForm();
        }
    });
    document.getElementById('delete-btn').addEventListener('click', async () => {
        const currentTab = document.querySelector('.tab-button.active').dataset.tab;
        if (currentTab === 'sales') {
            const selected = document.querySelector('#sales-table tbody tr.selected');
            if (!selected) {
                alert('삭제할 판매 기록을 선택하세요.');
                return;
            }
            const salesId = selected.dataset.salesId;
            if (confirm('선택한 판매 기록을 삭제하시겠습니까?')) {
                await fetchData(`/api/sales/${salesId}`, 'DELETE');
                loadSales();
            }
        } else {
            deleteProduct();
        }
    });
    // Product table edit button delegation
    const productTable = document.getElementById('product-table');
    productTable.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            e.stopPropagation();
            const productId = e.target.dataset.id;
            showProductForm(productId);
        }
    });
    // Delegate double-click on product rows to show detail dialog
    productTable.addEventListener('dblclick', (e) => {
        const tr = e.target.closest('tr');
        if (tr && tr.dataset.productId) {
            showProductDetail(tr.dataset.productId);
        }
    });
    document.getElementById('fav-only-btn').addEventListener('click', () => loadProducts({ is_favorite: true }));

    // Dialog Close Buttons
    document.querySelectorAll('.dialog .close-button').forEach(button => {
        button.addEventListener('click', (e) => hideDialog(e.target.closest('.dialog').id));
    });
    document.getElementById('detail-close-btn').addEventListener('click', () => hideDialog('product-detail-dialog'));
    document.getElementById('form-cancel-btn').addEventListener('click', () => hideDialog('product-form-dialog'));
    document.getElementById('sr-cancel-btn').addEventListener('click', () => hideDialog('sales-record-dialog'));
    document.getElementById('srd-close-btn').addEventListener('click', () => hideDialog('sales-record-detail-dialog'));

    // Product Form Submission
    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const productId = e.target.dataset.productId;
        const imagePathInput = document.getElementById('form-image-path');
        let finalImagePath = imagePathInput.value;

        const imageFile = document.getElementById('image-upload-input').files[0];
        if (imageFile) {
            const uploadResult = await uploadImage(imageFile);
            if (uploadResult) {
                finalImagePath = uploadResult.path;
            } else {
                return; // Stop if image upload failed
            }
        }

        const productData = {
            category: document.getElementById('form-category').value,
            supplier_name: document.getElementById('form-supplier-name').value,
            supplier_item_no: document.getElementById('form-supplier-item-no').value,
            product_code: document.getElementById('form-product-code').value,
            name: document.getElementById('form-name').value,
            karat: document.getElementById('form-karat').value,
            weight_g: parseFloat(document.getElementById('form-weight-g').value),
            size: document.getElementById('form-size').value,
            total_qb_qty: document.getElementById('form-total-qb-qty').value,
            basic_extra: join2(document.getElementById('form-basic-extra-left').value, document.getElementById('form-basic-extra-right').value),
            mid_back_bulim: join2(document.getElementById('form-mid-back-bulim-left').value, document.getElementById('form-mid-back-bulim-right').value),
            mid_back_labor: join2(document.getElementById('form-mid-back-labor-left').value, document.getElementById('form-mid-back-labor-right').value),
            cubic_labor: document.getElementById('form-cubic-labor').value,
            total_labor: document.getElementById('form-total-labor').value,
            discontinued: document.getElementById('form-discontinued').value === 'Y',
            stock_qty: parseInt(document.getElementById('form-stock-qty').value),
            image_path: finalImagePath,
            notes: document.getElementById('form-notes').value,
            is_favorite: document.getElementById('form-is-favorite').checked,
        };

        let result;
        if (productId && productId !== 'null') {
            result = await fetchData(`/api/products/${productId}`, 'PUT', productData);
        } else {
            result = await fetchData('/api/products/', 'POST', productData);
        }

        if (result) {
            alert('상품이 성공적으로 저장되었습니다.');
            hideDialog('product-form-dialog');
            loadProducts();
        }
    });

    // Sales Record Form Submission
    document.getElementById('sales-record-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const salesId = e.target.dataset.salesId;

        const salesRecordData = {
            customer_name: document.getElementById('sr-customer-name').value,
            sale_type: document.getElementById('sr-sale-type').value,
            return_reason: document.getElementById('sr-return-reason').value,
            purchase_market_price: parseInt(document.getElementById('sr-purchase-market-price').value),
            sale_market_price: parseInt(document.getElementById('sr-sale-market-price').value),
            final_sale_price: parseInt(document.getElementById('sr-final-sale-price').value),
            product_spplier: document.getElementById('sr-product-supplier').value,
            product_name: document.getElementById('sr-product-name').value,
            karat_unit: document.getElementById('sr-karat-unit').value,
            karat_g: document.getElementById('sr-karat-g').value,
            quantity: parseInt(document.getElementById('sr-quantity').value),
            color: document.getElementById('sr-color').value,
            size: document.getElementById('sr-size').value,
            main_stone_type: document.getElementById('sr-main-stone-type').value,
            main_stone_quantity: parseInt(document.getElementById('sr-main-stone-quantity').value),
            main_stone_purchase_price: parseInt(document.getElementById('sr-main-stone-purchase-price').value),
            main_stone_sale_price: parseInt(document.getElementById('sr-main-stone-sale-price').value),
            aux_stone_type: document.getElementById('sr-aux-stone-type').value,
            aux_stone_quantity: parseInt(document.getElementById('sr-aux-stone-quantity').value),
            aux_stone_purchase_price: parseInt(document.getElementById('sr-aux-stone-purchase-price').value),
            aux_stone_sale_price: parseInt(document.getElementById('sr-aux-stone-sale-price').value),
            basic_extra: join2(document.getElementById('sr-basic-extra-left').value, document.getElementById('sr-basic-extra-right').value),
            mid_back_bulim: join2(document.getElementById('sr-mid-back-bulim-left').value, document.getElementById('sr-mid-back-bulim-right').value),
            notes: document.getElementById('sr-notes').value,
            sale_date: document.getElementById('sr-sale-date').value,
        };

        let result;
        if (salesId && salesId !== 'null') {
            result = await fetchData(`/api/sales/${salesId}`, 'PUT', salesRecordData);
        } else {
            result = await fetchData('/api/sales/', 'POST', salesRecordData);
        }

        if (result) {
            alert('판매 기록이 성공적으로 저장되었습니다.');
            hideDialog('sales-record-dialog');
            loadSales();
        }
    });

    // Image upload button
    document.getElementById('browse-image-btn').addEventListener('click', () => {
        document.getElementById('image-upload-input').click();
    });

    document.getElementById('image-upload-input').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            document.getElementById('form-image-path').value = file.name; // Display file name
        }
    });

    // Initial Load
    loadProducts();
    // Set default dates for sales search
    const today = new Date();
    const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    document.getElementById('sales-start-date').value = oneMonthAgo.toISOString().split('T')[0];
    document.getElementById('sales-end-date').value = today.toISOString().split('T')[0];
});

// Global Load Functions
async function loadProducts(filters = {}) {
    const products = await fetchProducts(filters);
    if (products) {
        displayProducts(products);
    }
}

async function loadSales(filters = {}) {
    const salesRecords = await fetchSalesRecords(filters);
    if (salesRecords) {
        displaySalesRecords(salesRecords);
    }
}

async function deleteProduct() {
    const currentTab = document.querySelector('.tab-button.active').dataset.tab;
    if (currentTab === 'sales') {
        // 삭제할 판매 기록을 선택했는지 확인
        const selected = document.querySelector('#sales-table tbody tr.selected');
        if (!selected) {
            alert('삭제할 판매 기록을 선택하세요.');
            return;
        }
        const salesId = selected.dataset.salesId;
        if (confirm('선택한 판매 기록을 삭제하시겠습니까?')) {
            const result = await fetchData(`/api/sales/${salesId}`, 'DELETE');
            if (result) {
                alert('판매 기록이 삭제되었습니다.');
                loadSales();
            }
        }
    } else {
        // 상품 삭제 (이미지/목록 탭)
        let productId = null;
        if (currentTab === 'image') {
            const selectedItem = document.querySelector('.image-item.selected');
            if (selectedItem) {
                productId = selectedItem.dataset.productId;
            } else {
                alert('삭제할 상품을 선택하세요.');
                return;
            }
        } else if (currentTab === 'list') {
            const selectedRow = document.querySelector('#product-table tbody tr.selected');
            if (selectedRow) {
                productId = selectedRow.dataset.productId;
            } else {
                alert('삭제할 상품을 선택하세요.');
                return;
            }
        } else {
            alert('상품 삭제는 이미지 또는 목록 탭에서만 가능합니다.');
            return;
        }

        if (productId && confirm('정말 삭제하시겠습니까?')) {
            const result = await fetchData(`/api/products/${productId}`, 'DELETE');
            if (result) {
                alert('상품이 삭제되었습니다.');
                loadProducts();
            }
        }
    }
}

async function toggleFavorite(productId) {
    const result = await fetchData(`/api/products/${productId}/toggle_favorite`, 'POST');
    if (result) {
        loadProducts(); // Reload to update star icon
    }
}

// Add click listener for selecting items/rows (for delete functionality)
document.getElementById('image-list').addEventListener('click', (e) => {
    document.querySelectorAll('.image-item').forEach(item => item.classList.remove('selected'));
    const item = e.target.closest('.image-item');
    if (item) {
        item.classList.add('selected');
    }
});

document.querySelector('#product-table tbody').addEventListener('click', (e) => {
    document.querySelectorAll('#product-table tbody tr').forEach(row => row.classList.remove('selected'));
    const row = e.target.closest('tr');
    if (row) {
        row.classList.add('selected');
    }
});

document.querySelector('#sales-table tbody').addEventListener('click', (e) => {
    document.querySelectorAll('#sales-table tbody tr').forEach(row => row.classList.remove('selected'));
    const row = e.target.closest('tr');
    if (row) {
        row.classList.add('selected');
    }
});