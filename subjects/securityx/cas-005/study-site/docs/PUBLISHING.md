# GitHub Pages publishing

The learning repository deploys this directory with a dedicated GitHub Actions workflow. No npm/build framework is required.

Repository location:

`subjects/securityx/cas-005/study-site/`

Expected public URL after Pages is enabled:

`https://ualispublishing.github.io/learning/`

## First launch

1. Merge the SecurityX Pages pull request into `main`.
2. Open the repository on GitHub and go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open **Actions** and select **Deploy SecurityX study site to GitHub Pages**.
5. If no deployment is already running, choose **Run workflow** on `main`.
6. When the `deploy` job is green, open `https://ualispublishing.github.io/learning/`.

The workflow uploads only `subjects/securityx/cas-005/study-site/` as the Pages artifact. Keep the site labeled unofficial and do not add live-exam recollections, copied commercial questions, or unauthorized dumps.
