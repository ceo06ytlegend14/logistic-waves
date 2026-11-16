import re

with open('builtin-clone/views.py', 'r', encoding='utf-8') as f:
    code = f.read()

start_marker = "def auth_page(kind, next_path=\"\", error=\"\", message=\"\", preset_role=\"candidate\"):"
end_marker = "def account_shell(user, active, title, subtitle, content):"

idx1 = code.find(start_marker)
idx2 = code.find(end_marker)

if idx1 == -1 or idx2 == -1:
    print("Could not find markers:", idx1, idx2)
    exit(1)

new_auth_code = '''def auth_page(kind, next_path="", error="", message="", preset_role="candidate"):
    is_login = kind == "login"
    title = "Log In" if is_login else "Join Logistic Waves"
    action = "/auth/login" if is_login else "/auth/signup"
    title_text = "Welcome back" if is_login else "Create an account"
    subtitle_text = "Sign in to continue your journey." if is_login else "Start your global logistics journey today."
    switch_prefix = "Don't have an account yet?" if is_login else "Already have an account?"
    switch_label = "Create an account" if is_login else "Sign in"
    switch_href = e(url("/auth/signup", next=next_path)) if is_login else e(url("/auth/login", next=next_path))
    submit_btn_text = "Sign In" if is_login else "Create Account"
    
    if preset_role not in ("candidate", "employer", "admin"):
        preset_role = "candidate"
        
    signup_name_field = "" if is_login else f\'\'\'
      <div class="auth-input-group">
        <div class="auth-input-wrapper">
          <i class="fa-regular fa-user input-leading-icon"></i>
          <input id="nameInput" type="text" name="name" class="auth-field-control" placeholder="Enter your full name" required autocomplete="name">
        </div>
      </div>\'\'\'

    err_html = f\'\'\'
      <div class="auth-alert-box alert-error">
        <i class="fa-solid fa-circle-exclamation"></i>
        <span>{e(error)}</span>
      </div>\'\'\' if error else ""
      
    msg_html = f\'\'\'
      <div class="auth-alert-box alert-success">
        <i class="fa-solid fa-circle-check"></i>
        <span>{e(message)}</span>
      </div>\'\'\' if message else ""

    body = f\'\'\'
    <style>
      :root {{
        --header-promo-offset: 0px !important;
      }}
      body.auth-page-shell {{
        background: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
      }}
      body.auth-page-shell .promo-running-bar,
      body.auth-page-shell #promoRunningBar {{
        display: none !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
      }}
      body.auth-page-shell footer {{
        display: none !important;
      }}
      body.auth-page-shell #main-content {{
        flex: 1 0 auto !important;
        display: flex !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
      }}

      /* Top Header Refinements to Match Mockup */
      body.auth-page-shell .site-header {{
        background: #021e47 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
      }}
      body.auth-page-shell .site-header .search-trigger,
      body.auth-page-shell .site-header .employer-btn {{
        display: none !important;
      }}
      body.auth-page-shell .site-header .header-inner {{
        max-width: 100% !important;
        padding: 0 32px !important;
      }}

      /* Split Screen Layout (Matches Image Exactly) */
      .auth-split-wrapper {{
        display: grid !important;
        grid-template-columns: 63% 37% !important;
        width: 100% !important;
        min-height: calc(100vh - 66px) !important;
        background: #ffffff !important;
      }}

      /* Left Hero Panel (Visual Port Scene with Typography) */
      .auth-split-hero {{
        position: relative !important;
        background: url("/static/images/login_hero_split.jpg") center center / cover no-repeat !important;
        min-height: 600px !important;
        overflow: hidden !important;
      }}
      /* Clickable Overlay for 'Explore opportunities' */
      .auth-hero-click-link {{
        position: absolute !important;
        top: 48% !important;
        left: 6.5% !important;
        width: 240px !important;
        height: 44px !important;
        z-index: 5 !important;
        display: block !important;
        cursor: pointer !important;
        border-radius: 8px !important;
        transition: background 0.15s ease !important;
      }}
      .auth-hero-click-link:hover {{
        background: rgba(56, 189, 248, 0.12) !important;
      }}
      .sr-only {{
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0,0,0,0) !important;
        border: 0 !important;
      }}

      /* Right Card Column (Form) */
      .auth-split-card-col {{
        background: #ffffff !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 36px 48px !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
      }}
      .auth-card-inner {{
        width: 100% !important;
        max-width: 410px !important;
        margin: 0 auto !important;
      }}
      .auth-brand-badge {{
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        margin-bottom: 20px !important;
      }}
      .auth-brand-logo-img {{
        width: 32px !important;
        height: 32px !important;
        object-fit: contain !important;
      }}
      .auth-brand-title {{
        font-family: "Plus Jakarta Sans", -apple-system, sans-serif !important;
        font-size: 17px !important;
        font-weight: 800 !important;
        letter-spacing: 0.04em !important;
        color: #003875 !important;
      }}
      .auth-form-title {{
        font-family: "Plus Jakarta Sans", -apple-system, sans-serif !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 0 0 6px !important;
        letter-spacing: -0.03em !important;
        line-height: 1.15 !important;
      }}
      .auth-form-subtitle {{
        font-family: "Plus Jakarta Sans", sans-serif !important;
        font-size: 14.5px !important;
        color: #64748b !important;
        margin: 0 0 22px !important;
      }}

      /* Role Selector Tabs (Job Seeker / Employer) */
      .auth-role-tabs {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 6px !important;
        background: #f1f5f9 !important;
        padding: 4px !important;
        border-radius: 9999px !important;
        margin-bottom: 16px !important;
      }}
      .role-tab {{
        border: none !important;
        background: transparent !important;
        padding: 9px 16px !important;
        border-radius: 9999px !important;
        font-family: "Plus Jakarta Sans", sans-serif !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
      }}
      .role-tab.active {{
        background: #0060cc !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0, 96, 204, 0.25) !important;
      }}

      /* Quick Fill Bar */
      .auth-quick-fill-bar {{
        background: #f8fafc !important;
        border: 1px dashed #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
      }}
      .quick-fill-label {{
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        display: flex !important;
        align-items: center !important;
        gap: 5px !important;
      }}
      .quick-fill-chips {{
        display: flex !important;
        gap: 6px !important;
        flex-wrap: wrap !important;
      }}
      .chip-btn {{
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 5px !important;
        transition: all 0.15s ease !important;
      }}
      .chip-btn:hover {{
        background: #eff6ff !important;
        border-color: #93c5fd !important;
        color: #0060cc !important;
        transform: translateY(-1px) !important;
      }}
      .chip-btn.admin-chip {{
        background: #fef3c7 !important;
        border-color: #fde047 !important;
        color: #92400e !important;
      }}
      .chip-btn.admin-chip:hover {{
        background: #fef08a !important;
        border-color: #eab308 !important;
        color: #78350f !important;
      }}

      /* Inputs */
      .auth-input-group {{
        margin-bottom: 12px !important;
      }}
      .auth-input-wrapper {{
        position: relative !important;
        display: flex !important;
        align-items: center !important;
      }}
      .input-leading-icon {{
        position: absolute !important;
        left: 16px !important;
        font-size: 15px !important;
        color: #94a3b8 !important;
        pointer-events: none !important;
      }}
      .auth-field-control {{
        width: 100% !important;
        height: 48px !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0 16px 0 44px !important;
        font-size: 14.5px !important;
        color: #0f172a !important;
        background: #ffffff !important;
        box-sizing: border-box !important;
        outline: none !important;
        transition: all 0.2s ease !important;
      }}
      .auth-field-control:focus {{
        border-color: #0060cc !important;
        box-shadow: 0 0 0 3.5px rgba(0, 96, 204, 0.12) !important;
      }}
      .auth-field-control.has-toggle {{
        padding-right: 48px !important;
      }}
      .pwd-toggle-btn {{
        position: absolute !important;
        right: 12px !important;
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        cursor: pointer !important;
        padding: 6px !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: color 0.15s ease !important;
      }}
      .pwd-toggle-btn:hover {{
        color: #0f172a !important;
      }}

      /* Meta Options (Remember me / Forgot password) */
      .auth-meta-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin: 14px 0 20px !important;
        font-size: 13.5px !important;
      }}
      .auth-remember-checkbox {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        user-select: none !important;
      }}
      .auth-remember-checkbox input[type="checkbox"] {{
        width: 16px !important;
        height: 16px !important;
        accent-color: #0060cc !important;
        cursor: pointer !important;
        margin: 0 !important;
      }}
      .auth-forgot-link {{
        color: #0060cc !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        font-size: 13px !important;
      }}
      .auth-forgot-link:hover {{
        text-decoration: underline !important;
      }}

      /* Submit Button */
      .auth-submit-btn {{
        width: 100% !important;
        height: 48px !important;
        background: #0060cc !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: "Plus Jakarta Sans", sans-serif !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 14px rgba(0, 96, 204, 0.3) !important;
      }}
      .auth-submit-btn:hover {{
        background: #004fb0 !important;
        box-shadow: 0 6px 18px rgba(0, 96, 204, 0.45) !important;
        transform: translateY(-1px) !important;
      }}
      .auth-submit-btn .btn-arrow {{
        display: inline-block !important;
        transition: transform 0.2s ease !important;
      }}
      .auth-submit-btn:hover .btn-arrow {{
        transform: translateX(4px) !important;
      }}

      /* SSO Divider */
      .auth-sso-divider {{
        display: flex !important;
        align-items: center !important;
        text-align: center !important;
        margin: 18px 0 14px !important;
        color: #94a3b8 !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
      }}
      .auth-sso-divider::before,
      .auth-sso-divider::after {{
        content: "" !important;
        flex: 1 !important;
        border-bottom: 1px solid #e2e8f0 !important;
      }}
      .auth-sso-divider span {{
        padding: 0 12px !important;
      }}

      /* SSO Row */
      .auth-sso-row {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 12px !important;
        margin-bottom: 20px !important;
      }}
      .sso-btn {{
        height: 44px !important;
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0 14px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
      }}
      .sso-btn:hover {{
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        transform: translateY(-1px) !important;
      }}

      /* Bottom Switch */
      .auth-bottom-switch {{
        text-align: center !important;
        font-size: 13.5px !important;
        color: #475569 !important;
      }}
      .switch-link {{
        color: #0060cc !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        margin-left: 4px !important;
      }}
      .switch-link:hover {{
        text-decoration: underline !important;
      }}

      /* Alert Boxes */
      .auth-alert-box {{
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 12px 14px !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-bottom: 14px !important;
      }}
      .alert-error {{
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #b91c1c !important;
      }}
      .alert-success {{
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #15803d !important;
      }}
      .demo-highlight {{
        background-color: #ecfdf5 !important;
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3.5px rgba(16, 185, 129, 0.15) !important;
      }}

      @media (max-width: 992px) {{
        .auth-split-wrapper {{
          grid-template-columns: 1fr !important;
        }}
        .auth-split-hero {{
          min-height: 320px !important;
        }}
        .auth-split-card-col {{
          padding: 32px 20px !important;
        }}
      }}
    </style>

    <div class="auth-split-wrapper">
      <!-- Left Column: Hero Port Visual (From User Mockup) -->
      <div class="auth-split-hero">
        <a href="/jobs" class="auth-hero-click-link" title="Explore logistics opportunities">
          <span class="sr-only">Explore opportunities</span>
        </a>
      </div>

      <!-- Right Column: Login Card -->
      <div class="auth-split-card-col">
        <div class="auth-card-inner">
          
          <!-- Brand Logo at top of form -->
          <div class="auth-brand-badge">
            <img src="/static/images/logo_emblem.png" alt="Logistics Waves" class="auth-brand-logo-img">
            <span class="auth-brand-title">LOGISTICS WAVES</span>
          </div>

          <!-- Welcome Title -->
          <h2 class="auth-form-title">{title_text}</h2>
          <p class="auth-form-subtitle">{subtitle_text}</p>

          <!-- Role Selector Capsule Tabs -->
          <div class="auth-role-tabs">
            <button type="button" class="role-tab {\'active\' if preset_role != \'employer\' else \'\'}" id="roleCandidateBtn" onclick="selectAuthRole(\'candidate\')">
              <i class="fa-solid fa-user"></i>
              <span>Job Seeker</span>
            </button>
            <button type="button" class="role-tab {\'active\' if preset_role == \'employer\' else \'\'}" id="roleEmployerBtn" onclick="selectAuthRole(\'employer\')">
              <i class="fa-solid fa-building"></i>
              <span>Employer</span>
            </button>
          </div>

          <!-- Quick Fill Bar for Admin & Demos -->
          <div class="auth-quick-fill-bar">
            <span class="quick-fill-label"><i class="fa-solid fa-key"></i> Quick Fill Credentials:</span>
            <div class="quick-fill-chips">
              <button type="button" class="chip-btn admin-chip" onclick="fillCredentials(\'admin@logisticwaves.com\', \'Admin@Waves2026!\', \'System Administrator\', \'admin\')" title="Fill Admin Credentials">
                <i class="fa-solid fa-shield-halved"></i> Admin
              </button>
              <button type="button" class="chip-btn" onclick="fillCredentials(\'employer@demo.com\', \'demo1234\', \'Morgan Employer\', \'employer\')" title="Fill Employer Credentials">
                <i class="fa-solid fa-building-user"></i> Employer
              </button>
              <button type="button" class="chip-btn" onclick="fillCredentials(\'candidate@demo.com\', \'demo1234\', \'Alex Candidate\', \'candidate\')" title="Fill Job Seeker Credentials">
                <i class="fa-solid fa-user-check"></i> Job Seeker
              </button>
            </div>
          </div>

          {err_html}
          {msg_html}

          <!-- Main Form -->
          <form method="post" action="{action}" id="authMainForm">
            <input type="hidden" name="next" value="{e(next_path)}">
            <input type="hidden" name="role" id="authRoleInput" value="{preset_role}">

            {signup_name_field}

            <!-- Email Field -->
            <div class="auth-input-group">
              <div class="auth-input-wrapper">
                <i class="fa-regular fa-envelope input-leading-icon"></i>
                <input id="emailInput" type="email" name="email" class="auth-field-control" placeholder="Enter your email address" required autocomplete="username">
              </div>
            </div>

            <!-- Password Field -->
            <div class="auth-input-group">
              <div class="auth-input-wrapper">
                <i class="fa-solid fa-lock input-leading-icon"></i>
                <input id="pwdInput" type="password" name="password" class="auth-field-control has-toggle" placeholder="Enter your password" required autocomplete="current-password">
                <button type="button" class="pwd-toggle-btn" onclick="togglePasswordVisibility()" aria-label="Toggle password visibility">
                  <i id="eyeIcon" class="fa-regular fa-eye-slash"></i>
                </button>
              </div>
            </div>

            <!-- Options row -->
            <div class="auth-meta-row">
              <label class="auth-remember-checkbox">
                <input type="checkbox" name="remember" checked>
                <span>Remember me for 30 days</span>
              </label>
              <a href="javascript:void(0)" onclick="forgotPasswordHint()" class="auth-forgot-link">Forgot password?</a>
            </div>

            <!-- Submit Button -->
            <button class="auth-submit-btn" type="submit">
              <span>{submit_btn_text}</span>
              <span class="btn-arrow">&rarr;</span>
            </button>
          </form>

          <!-- SSO Divider -->
          <div class="auth-sso-divider">
            <span>or continue with</span>
          </div>

          <!-- SSO Buttons -->
          <div class="auth-sso-row">
            <button type="button" class="sso-btn" onclick="fillCredentials(\'candidate@demo.com\', \'demo1234\', \'Alex Candidate\', \'candidate\')">
              <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/><path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/><path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.03 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/><path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/></svg>
              <span>Google</span>
            </button>
            <button type="button" class="sso-btn" onclick="fillCredentials(\'employer@demo.com\', \'demo1234\', \'Morgan Employer\', \'employer\')">
              <i class="fa-brands fa-linkedin" style="color: #0a66c2; font-size: 18px;"></i>
              <span>LinkedIn</span>
            </button>
          </div>

          <!-- Bottom Account Switch -->
          <div class="auth-bottom-switch">
            <span>{switch_prefix}</span>
            <a href="{switch_href}" class="switch-link">{switch_label} &rarr;</a>
          </div>

        </div>
      </div>
    </div>

    <script>
      function selectAuthRole(role) {{
        var roleInput = document.getElementById('authRoleInput');
        if (roleInput) roleInput.value = role;
        
        var candBtn = document.getElementById('roleCandidateBtn');
        var empBtn = document.getElementById('roleEmployerBtn');
        if (role === 'employer') {{
          if (candBtn) candBtn.classList.remove('active');
          if (empBtn) empBtn.classList.add('active');
        }} else {{
          if (candBtn) candBtn.classList.add('active');
          if (empBtn) empBtn.classList.remove('active');
        }}
      }}

      function fillCredentials(email, pwd, name, role) {{
        var emailInput = document.getElementById('emailInput');
        var pwdInput = document.getElementById('pwdInput');
        var nameInput = document.getElementById('nameInput');
        
        if (emailInput) {{
          emailInput.value = email;
          emailInput.classList.add('demo-highlight');
        }}
        if (pwdInput) {{
          pwdInput.value = pwd;
          pwdInput.classList.add('demo-highlight');
        }}
        if (nameInput) {{
          nameInput.value = name;
          nameInput.classList.add('demo-highlight');
        }}
        selectAuthRole(role === 'admin' ? 'employer' : role);
        
        setTimeout(function() {{
          if (emailInput) emailInput.classList.remove('demo-highlight');
          if (pwdInput) pwdInput.classList.remove('demo-highlight');
          if (nameInput) nameInput.classList.remove('demo-highlight');
        }}, 1200);
      }}

      function togglePasswordVisibility() {{
        var pwd = document.getElementById('pwdInput');
        var icon = document.getElementById('eyeIcon');
        if (!pwd || !icon) return;
        if (pwd.type === 'password') {{
          pwd.type = 'text';
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }} else {{
          pwd.type = 'password';
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        }}
      }}

      function forgotPasswordHint() {{
        alert('Credentials:\\n• Admin: admin@logisticwaves.com (Password: Admin@Waves2026!)\\n• Employer: employer@demo.com (Password: demo1234)\\n• Job Seeker: candidate@demo.com (Password: demo1234)\\n\\nClick any Quick Fill button to populate credentials instantly!');
      }}
    </script>
    \'\'\'
    return layout(title, body, None, page_class="auth-page-shell", description="Log in or create a free account.")
'''

updated_code = code[:idx1] + new_auth_code + code[idx2:]

with open('builtin-clone/views.py', 'w', encoding='utf-8') as f:
    f.write(updated_code)

print("Successfully replaced auth_page in views.py!")
