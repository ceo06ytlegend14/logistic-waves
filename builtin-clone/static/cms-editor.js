/**
 * LOGISTIC WAVES - Unified CMS Editor Scripts
 * 3-Column Modals, Tag/Skill Chips, Image Uploaders, Tab Switching, Publishing Controls
 */

function openCmsModal(modalId) {
  var modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  if (window.initCmsRichEditor) window.initCmsRichEditor();
}

function closeCmsModal(modalId) {
  var modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
  if (!document.querySelector('.cms-modal-backdrop.active, .admin-modal-backdrop.active')) {
    document.body.style.overflow = '';
  }
}

function closeAllCmsModals() {
  document.querySelectorAll('.cms-modal-backdrop, .admin-modal-backdrop').forEach(function(m) {
    m.classList.remove('active');
  });
  document.body.style.overflow = '';
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeAllCmsModals();
});

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('cms-modal-backdrop') || e.target.classList.contains('admin-modal-backdrop')) {
    closeAllCmsModals();
  }
});

function switchCmsTab(btn, paneId) {
  var modal = btn.closest('.cms-modal-dialog');
  if (!modal) return;
  modal.querySelectorAll('.cms-side-nav-btn').forEach(function(b) { b.classList.remove('active'); });
  modal.querySelectorAll('.cms-tab-pane').forEach(function(p) { p.classList.remove('active'); });
  btn.classList.add('active');
  var pane = modal.querySelector('#' + paneId);
  if (pane) pane.classList.add('active');
}

function handleCmsImageUpload(fileInput, targetInputId, previewImgId) {
  if (!fileInput.files || !fileInput.files[0]) return;
  var file = fileInput.files[0];
  var reader = new FileReader();
  reader.onload = function(e) {
    var img = new Image();
    img.onload = function() {
      var maxW = 1200, maxH = 800;
      var w = img.width, h = img.height;
      if (w > maxW || h > maxH) {
        if (w / maxW > h / maxH) { h = Math.round(h * (maxW / w)); w = maxW; }
        else { w = Math.round(w * (maxH / h)); h = maxH; }
      }
      var canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      var optimized = canvas.toDataURL('image/jpeg', 0.85);
      var target = document.getElementById(targetInputId);
      var prev = document.getElementById(previewImgId);
      if (prev) prev.src = optimized;
      var csrf = document.querySelector('meta[name="csrf-token"]');
      fetch('/admin/media/upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf ? csrf.content : ''},
        body: JSON.stringify({data_uri: optimized})
      }).then(function(res) { return res.json(); }).then(function(data) {
        if (!data.ok || !data.url) throw new Error(data.error || 'Upload failed.');
        if (target) target.value = data.url;
        if (prev) prev.src = data.url;
      }).catch(function(err) {
        if (target) target.value = '';
        if (window.showToast) window.showToast(err.message || 'Image upload failed.', true);
        else alert(err.message || 'Image upload failed.');
      });
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function updateCmsImagePreview(url, previewImgId) {
  var prev = document.getElementById(previewImgId);
  if (!prev) return;
  prev.src = (url && url.trim()) ? url.trim() : '/static/images/fw_today_1.jpg';
}

function toggleCmsUrlInput(boxId) {
  var box = document.getElementById(boxId);
  if (!box) return;
  box.style.display = (box.style.display === 'none' || !box.style.display) ? 'flex' : 'none';
}

function syncCmsChips(containerId, hiddenInputId) {
  var container = document.getElementById(containerId);
  var hidden = document.getElementById(hiddenInputId);
  if (!container || !hidden) return;
  var vals = [];
  container.querySelectorAll('.cms-chip-pill').forEach(function(pill) {
    var txt = pill.getAttribute('data-val');
    if (txt) vals.push(txt);
  });
  hidden.value = vals.join(', ');
}

function removeCmsChip(btn, containerId, hiddenInputId) {
  var pill = btn.closest('.cms-chip-pill');
  if (pill) pill.remove();
  syncCmsChips(containerId, hiddenInputId);
}

function addCmsChip(containerId, hiddenInputId, label) {
  var val = prompt('Add ' + (label || 'tag') + ':');
  if (!val || !val.trim()) return;
  val = val.trim();
  var container = document.getElementById(containerId);
  var addBtn = container ? container.querySelector('.cms-chip-add-btn') : null;
  if (!container || !addBtn) return;
  var span = document.createElement('span');
  span.className = 'cms-chip-pill';
  span.setAttribute('data-val', val);
  span.innerHTML = val.replace(/</g, '&lt;') + ' <button type="button" class="cms-chip-remove" onclick="removeCmsChip(this, \'' + containerId + '\', \'' + hiddenInputId + '\')">&times;</button>';
  container.insertBefore(span, addBtn);
  syncCmsChips(containerId, hiddenInputId);
}

function syncCmsSocialLinks(form) {
  var li = form.querySelector('.cms-social-linkedin');
  var yt = form.querySelector('.cms-social-youtube');
  var fb = form.querySelector('.cms-social-facebook');
  var hidden = form.querySelector('input[name="social_links"]');
  if (hidden && (li || yt || fb)) {
    var parts = [li ? li.value.trim() : '', yt ? yt.value.trim() : '', fb ? fb.value.trim() : ''].filter(Boolean);
    hidden.value = parts.join(', ');
  }
}

function submitCmsPublish(formId, targetStatus) {
  var form = document.getElementById(formId);
  if (!form) return;
  if (targetStatus === 'archived') {
    if (!confirm('Are you sure you want to archive this item? It will be hidden from public listings.')) return;
  }
  if (window.tinymce) tinymce.triggerSave();
  syncCmsSocialLinks(form);
  var statusEl = form.querySelector('[name="status"]');
  if (statusEl && targetStatus) statusEl.value = targetStatus;
  form.submit();
}

function previewCmsItem(url) {
  if (url) window.open(url, '_blank');
}

function insertCmsDevicePhoto(fileInput, editorId) {
  if (!fileInput.files || !fileInput.files[0]) return;
  var file = fileInput.files[0];
  var reader = new FileReader();
  reader.onload = function(e) {
    var img = new Image();
    img.onload = function() {
      var maxW = 1200, maxH = 900;
      var w = img.width, h = img.height;
      if (w > maxW || h > maxH) {
        if (w / maxW > h / maxH) { h = Math.round(h * (maxW / w)); w = maxW; }
        else { w = Math.round(w * (maxH / h)); h = maxH; }
      }
      var canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      var optimized = canvas.toDataURL('image/jpeg', 0.86);
      var figureHtml = '<figure style="margin:20px auto;text-align:center;"><img src="' + optimized + '" alt="' + file.name + '" style="max-width:100%;height:auto;border-radius:10px;" /></figure><p>&nbsp;</p>';
      var ed = window.tinymce ? tinymce.get(editorId) : null;
      if (ed) { ed.insertContent(figureHtml); ed.focus(); }
      fileInput.value = '';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

window.initCmsRichEditor = function() {
  if (typeof tinymce === 'undefined') return;
  var editors = document.querySelectorAll('.cms-rich-editor');
  if (!editors.length) return;
  tinymce.init({
    selector: '.cms-rich-editor',
    min_height: 240,
    menubar: false,
    plugins: 'image link lists table code media wordcount autolink',
    toolbar: 'undo redo | blocks | bold italic underline | alignleft aligncenter alignright | bullist numlist | image link | removeformat',
    content_style: 'body { font-family: Inter, -apple-system, sans-serif; font-size: 14px; color: #1e293b; line-height: 1.6; padding: 10px; } img { max-width: 100%; height: auto; border-radius: 8px; }',
    paste_data_images: true,
    automatic_uploads: true,
    setup: function(editor) {
      editor.on('change keyup', function() { editor.save(); });
    }
  });
};

document.addEventListener('DOMContentLoaded', function() {
  if (window.initCmsRichEditor) window.initCmsRichEditor();
  var params = new URLSearchParams(window.location.search);
  var msg = params.get('msg');
  var err = params.get('err');
  if (msg || err) {
    if (window.showToast) {
      window.showToast(msg || err);
    } else {
      var toast = document.getElementById('toast');
      if (toast) {
        toast.textContent = msg || err;
        toast.className = 'toast show ' + (err ? 'toast-err' : 'toast-success');
        setTimeout(function() { toast.className = 'toast'; }, 4000);
      }
    }
    params.delete('msg');
    params.delete('err');
    var newQuery = params.toString() ? ('?' + params.toString()) : '';
    window.history.replaceState({}, '', window.location.pathname + newQuery + window.location.hash);
  }
});

/* ==========================================================================
   JOB MEDIA & GALLERY HELPER FUNCTIONS
   ========================================================================== */
function getJobGalleryItems(prefix) {
  var hidden = document.getElementById(prefix + '-gallery-images');
  if (!hidden || !hidden.value) return [];
  return hidden.value.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
}

function syncJobGalleryHidden(prefix, items) {
  var hidden = document.getElementById(prefix + '-gallery-images');
  if (hidden) hidden.value = items.join(', ');
  renderJobGalleryGrid(prefix, items.join(', '));
}

function renderJobGalleryGrid(prefix, csvList) {
  var container = document.getElementById(prefix + '-gallery-grid');
  var hidden = document.getElementById(prefix + '-gallery-images');
  if (!container) return;
  var items = (csvList !== undefined ? csvList : (hidden ? hidden.value : '')).split(',').map(function(s) { return s.trim(); }).filter(Boolean);
  if (hidden && csvList !== undefined) hidden.value = items.join(', ');

  if (!items.length) {
    container.innerHTML = '<div class="cms-gallery-empty"><i class="fa-regular fa-images"></i><span>No gallery photos added yet. Click &ldquo;Load Logistics Gallery&rdquo; or upload workplace photos.</span></div>';
    return;
  }

  var html = items.map(function(url, idx) {
    var safeUrl = url.replace(/'/g, '&#39;').replace(/"/g, '&quot;');
    return '<div class="cms-gallery-card">' +
      '<img src="' + safeUrl + '" alt="Photo ' + (idx + 1) + '" onerror="this.onerror=null;this.src=\'/static/images/fw_today_1.jpg\'">' +
      '<button type="button" class="cms-gallery-remove" onclick="removeJobGalleryPhoto(\'' + prefix + '\', ' + idx + ')" title="Remove photo">&times;</button>' +
      '<div class="cms-gallery-badge">Photo ' + (idx + 1) + '</div>' +
      '</div>';
  }).join('');
  container.innerHTML = html;
}

function addJobGalleryPhoto(prefix, url) {
  if (!url || !url.trim()) return;
  var items = getJobGalleryItems(prefix);
  items.push(url.trim());
  syncJobGalleryHidden(prefix, items);
}

function addJobGalleryPhotoPrompt(prefix) {
  var url = prompt('Enter image URL for job gallery:');
  if (url && url.trim()) {
    addJobGalleryPhoto(prefix, url.trim());
  }
}

function removeJobGalleryPhoto(prefix, index) {
  var items = getJobGalleryItems(prefix);
  if (index >= 0 && index < items.length) {
    items.splice(index, 1);
    syncJobGalleryHidden(prefix, items);
  }
}

function seedJobGalleryPresets(prefix) {
  var presets = [
    '/static/images/port_logistics_1.jpg',
    '/static/images/port_logistics_2.jpg',
    '/static/images/hero_transport_clean.jpg',
    '/static/images/fw_today_3.jpg',
    '/static/images/arch_glass_office.jpg',
    '/static/images/arch_office_team.jpg'
  ];
  syncJobGalleryHidden(prefix, presets);
  if (window.showToast) window.showToast('Loaded 6 logistics workplace photos!');
}

function clearJobGallery(prefix) {
  if (confirm('Clear all gallery photos for this job?')) {
    syncJobGalleryHidden(prefix, []);
  }
}

function uploadJobGalleryPhoto(fileInput, prefix) {
  if (!fileInput.files || !fileInput.files[0]) return;
  var file = fileInput.files[0];
  var reader = new FileReader();
  reader.onload = function(e) {
    var img = new Image();
    img.onload = function() {
      var maxW = 1200, maxH = 800;
      var w = img.width, h = img.height;
      if (w > maxW || h > maxH) {
        if (w / maxW > h / maxH) { h = Math.round(h * (maxW / w)); w = maxW; }
        else { w = Math.round(w * (maxH / h)); h = maxH; }
      }
      var canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      var optimized = canvas.toDataURL('image/jpeg', 0.85);

      var csrf = document.querySelector('meta[name="csrf-token"]');
      fetch('/admin/media/upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf ? csrf.content : ''},
        body: JSON.stringify({data_uri: optimized})
      }).then(function(res) { return res.json(); }).then(function(data) {
        if (!data.ok || !data.url) throw new Error(data.error || 'Upload failed.');
        addJobGalleryPhoto(prefix, data.url);
      }).catch(function() {
        addJobGalleryPhoto(prefix, optimized);
      });
      fileInput.value = '';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function setJobCoverPreset(prefix, url) {
  var inp = document.getElementById(prefix + '-image-url');
  var prev = document.getElementById(prefix + '-image-preview');
  if (inp) inp.value = url;
  if (prev) prev.src = url;
}
