# 🚀 GitHub Push Instructions

Follow these steps to push your project to GitHub:

## Step 1: Navigate to Your Project Directory

```bash
cd /path/to/google_ads_api_checker
```

## Step 2: Initialize Git Repository

```bash
git init
```

## Step 3: Add All Files

```bash
git add .
```

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Google Ads Creative Validator"
```

## Step 5: Add Remote Repository

```bash
git remote add origin https://github.com/nstanley-ui/google_ads_api_checker.git
```

## Step 6: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 🔐 Authentication Options

### Option A: Personal Access Token (Recommended)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all)
4. Generate and copy the token
5. When prompted for password, paste the token

### Option B: SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Add this to GitHub: https://github.com/settings/keys

# Use SSH remote instead
git remote set-url origin git@github.com:nstanley-ui/google_ads_api_checker.git
```

---

## ✅ Verify Success

After pushing, visit: https://github.com/nstanley-ui/google_ads_api_checker

You should see:
- ✅ All project files
- ✅ README.md rendered on the homepage
- ✅ .gitignore protecting sensitive files

---

## 📝 One-Line Command (If Already Initialized)

If you already have the files locally:

```bash
cd /path/to/google_ads_api_checker && \
git add . && \
git commit -m "Initial commit: Google Ads Creative Validator" && \
git branch -M main && \
git push -u origin main
```

---

## 🔄 Making Future Updates

```bash
# After making changes
git add .
git commit -m "Description of changes"
git push
```

---

## 🆘 Troubleshooting

### Error: "Repository not found"
- Verify you have access to: https://github.com/nstanley-ui/google_ads_api_checker
- Check repository name spelling
- Ensure you're logged in to the correct GitHub account

### Error: "Authentication failed"
- Use a Personal Access Token instead of password
- Or set up SSH authentication

### Error: "Remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/nstanley-ui/google_ads_api_checker.git
```

### Want to Start Fresh?
```bash
rm -rf .git
git init
# Then follow steps 3-6 above
```
