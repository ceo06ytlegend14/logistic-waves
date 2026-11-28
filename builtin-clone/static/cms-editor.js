/**
 * LOGISTIC WAVES - CMS Editor Client Scripts
 * Modal management, publishing workflows, TinyMCE photo galleries, image uploads
 */

function openCmsModal(modalId) {
  var modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Initialize TinyMCE if an uninitialized rich-editor is present inside
  if (window.initCmsRichEditor) {
    window.initCmsRichEditor();
  }
}

function closeCmsModal(modalId) {
  var modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
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

// ESC Key & Outside Click dismiss
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeAllCmsModals();
});

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('cms-modal-backdrop') || e.target.classList.contains('admin-modal-backdrop')) {
    closeAllCmsModals();
  }
});

// Image File Upload with Client-Side Resize
function handleCmsImageUpload(fileInput, targetInputId, previewImgId) {
  if (!fileInput.files || !fileInput.files[0]) return;
  var file = fileInput.files[0];
  var reader = new FileReader();
  reader.onload = function(e) {
    var rawData = e.target.result;
    var img = new Image();
    img.onload = function() {
      var maxW = 1200;
      var maxH = 800;
      var w = img.width;
      var h = img.height;
      if (w > maxW || h > maxH) {
        if (w / maxW > h / maxH) {
          h = Math.round(h * (maxW / w));
          w = maxW;
        } else {
          w = Math.round(w * (maxH / h));
          h = maxH;
        }
      }
      var canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      var ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      var optimized = canvas.toDataURL('image/jpeg', 0.85);
      var targetInput = document.getElementById(targetInputId);
      if (targetInput) targetInput.value = optimized;
      var prev = document.getElementById(previewImgId);
      if (prev) prev.src = optimized;
    };
    img.src = rawData;
  };
  reader.readAsDataURL(file);
}

function updateCmsImagePreview(url, previewImgId) {
  var prev = document.getElementById(previewImgId);
  if (!prev) return;
  if (!url || !url.trim()) {
    prev.src = '/static/images/fw_today_1.jpg';
  } else {
    prev.src = url.trim();
  }
}

function clearCmsImageUpload(targetInputId, previewImgId) {
  var target = document.getElementById(targetInputId);
  if (target) target.value = '';
  var prev = document.getElementById(previewImgId);
  if (prev) {
    prev.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="70" viewBox="0 0 100 70"><rect width="100%" height="100%" fill="%23f1f5f9"/><text x="50%" y="54%" font-family="sans-serif" font-size="11" fill="%2394a3b8" text-anchor="middle">No Image</text></svg>';
  }
}

function setCmsPresetImage(targetInputId, previewImgId, url) {
  var target = document.getElementById(targetInputId);
  if (target) target.value = url;
  updateCmsImagePreview(url, previewImgId);
}

// Publishing Workflows: Save Changes, Save Draft, Publish, Archive, Preview
function submitCmsPublish(formId, targetStatus) {
  var form = document.getElementById(formId);
  if (!form) return;

  if (targetStatus === 'archived') {
    if (!confirm('Are you sure you want to archive this content? It will no longer appear on public listings.')) {
      return;
    }
  }

  // Sync TinyMCE if present
  if (window.tinymce) {
    tinymce.triggerSave();
  }

  // Set hidden status input
  var statusInput = form.querySelector('input[name="status"]');
  if (!statusInput) {
    statusInput = document.createElement('input');
    statusInput.type = 'hidden';
    statusInput.name = 'status';
    form.appendChild(statusInput);
  }
  if (targetStatus) {
    statusInput.value = targetStatus;
  }

  form.submit();
}

function previewCmsItem(url) {
  if (url) {
    window.open(url, '_blank');
  }
}

// WYSIWYG TinyMCE Photo Insertion & Galleries
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
      var ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      var optimized = canvas.toDataURL('image/jpeg', 0.86);
      var figureHtml = '<figure style="margin:24px auto;text-align:center;"><img src="' + optimized + '" alt="' + file.name + '" style="max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;" /><figcaption style="font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;">' + file.name + '</figcaption></figure><p>&nbsp;</p>';
      var ed = window.tinymce ? tinymce.get(editorId) : null;
      if (ed) {
        ed.insertContent(figureHtml);
        ed.focus();
      }
      fileInput.value = '';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function insertCmsGallery(editorId, mode) {
  var ed = window.tinymce ? tinymce.get(editorId) : null;
  var html = '';
  if (mode === 'single') {
    var promptUrl = prompt('Enter image URL (Unsplash or web link):', 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80');
    if (!promptUrl) return;
    html = '<figure style="margin:24px auto;text-align:center;"><img src="' + promptUrl + '" alt="Logistics Operations" style="max-width:100%;height:auto;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);display:block;margin:0 auto;" /><figcaption style="font-size:12.5px;color:#64748b;font-style:italic;text-align:center;margin-top:6px;">Logistics Terminal Operations</figcaption></figure><p>&nbsp;</p>';
  } else if (mode === 'gallery2') {
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin:28px 0;"><figure style="margin:0;"><img src="https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80" alt="Berth Operations &amp; Gantry Crane" style="width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);" /><figcaption style="font-size:12px;color:#64748b;text-align:center;margin-top:4px;">Berth Operations &amp; Gantry Crane</figcaption></figure><figure style="margin:0;"><img src="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80" alt="Automated Cargo Vessel" style="width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.08);" /><figcaption style="font-size:12px;color:#64748b;text-align:center;margin-top:4px;">Automated Cargo Vessel</figcaption></figure></div><p>&nbsp;</p>';
  } else if (mode === 'gallery3') {
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:14px;margin:28px 0;"><figure style="margin:0;"><img src="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=600&q=80" alt="Intermodal Container Yard" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.08);" /><figcaption style="font-size:11.5px;color:#64748b;text-align:center;margin-top:4px;">Intermodal Container Yard</figcaption></figure><figure style="margin:0;"><img src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=600&q=80" alt="Fleet Control Center" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.08);" /><figcaption style="font-size:11.5px;color:#64748b;text-align:center;margin-top:4px;">Fleet Control Center</figcaption></figure><figure style="margin:0;"><img src="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=600&q=80" alt="Air Cargo Logistics Hub" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.08);" /><figcaption style="font-size:11.5px;color:#64748b;text-align:center;margin-top:4px;">Air Cargo Logistics Hub</figcaption></figure></div><p>&nbsp;</p>';
  }

  if (ed) {
    ed.insertContent(html);
    ed.focus();
  } else {
    var txt = document.getElementById(editorId);
    if (txt) {
      txt.value += html;
      txt.focus();
    }
  }
}

// TinyMCE Init for CMS Modals
window.initCmsRichEditor = function() {
  if (typeof tinymce === 'undefined') return;
  var editors = document.querySelectorAll('.cms-rich-editor');
  if (!editors.length) return;

  tinymce.init({
    selector: '.cms-rich-editor',
    min_height: 380,
    menubar: false,
    plugins: 'image link lists table code media wordcount autolink',
    toolbar: 'undo redo | blocks | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | image link table | removeformat code',
    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 15px; color: #1e293b; line-height: 1.65; padding: 12px; } img { max-width: 100%; height: auto; border-radius: 8px; cursor: pointer; } mark, span[style*="background-color"] { border-radius: 3px; padding: 1px 4px; }',
    image_advtab: true,
    image_caption: true,
    image_dimensions: true,
    paste_data_images: true,
    automatic_uploads: true,
    images_upload_handler: function(blobInfo, progress) {
      return new Promise(function(resolve, reject) {
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
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, w, h);
            resolve(canvas.toDataURL('image/jpeg', 0.86));
          };
          img.onerror = function() { resolve(e.target.result); };
          img.src = e.target.result;
        };
        reader.onerror = function(err) { reject('Upload error: ' + err); };
        reader.readAsDataURL(blobInfo.blob());
      });
    },
    setup: function(editor) {
      editor.on('change keyup', function() { editor.save(); });
    }
  });
};

// Auto toast & URL cleaner
document.addEventListener('DOMContentLoaded', function() {
  if (window.initCmsRichEditor) {
    window.initCmsRichEditor();
  }

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
    // Clean URL without reloading
    params.delete('msg');
    params.delete('err');
    var newQuery = params.toString() ? ('?' + params.toString()) : '';
    window.history.replaceState({}, '', window.location.pathname + newQuery + window.location.hash);
  }
});
