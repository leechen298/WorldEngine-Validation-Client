import type { BranchSummary } from "../api/types";

export function TimelineBranchList({ branches }: { branches: BranchSummary[] }) {
  return (
    <section className="page-card">
      <h3>分支列表</h3>
      <ul className="session-list">
        {branches.map((branch) => (
          <li className="branch-item" key={branch.id}>
            {branch.branch_name} (tick {branch.tick})
          </li>
        ))}
      </ul>
    </section>
  );
}
