
---

## Summary Table

| Step                   | Command/Action                                            |
|------------------------|----------------------------------------------------------|
| Create feature branch  | `git checkout -b feature/your-feature`                   |
| Commit changes         | `git add .`<br>`git commit -m "Describe your change"`    |
| Push branch            | `git push -u origin feature/your-feature`                |
| Open & merge PR        | Use GitHub UI                                            |
| Update local main      | `git checkout main`<br>`git pull origin main`            |

---

## Why Use This Workflow?

- **Keeps `main` stable:** Only completed, tested features go into production.
- **Isolates work:** Each feature or fix is separate, making it easy to manage or revert.
- **Documents changes:** Pull requests provide a clear history of what changed and why.
- **Professional and scalable:** Prepares your workflow for future team collaboration.

---

## Tips

- Use descriptive branch and commit names.
- Regularly push your branches to GitHub for backup and version history.
- Even as a solo developer, this workflow helps maintain a clean, professional project history.

