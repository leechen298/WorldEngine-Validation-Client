import type { BranchSummary } from "../api/types";

interface TimelineBranchListProps {
  branches: BranchSummary[];
  selectedBranchId?: string;
  onSelect?: (branch: BranchSummary) => void;
}

export function TimelineBranchList({ branches, selectedBranchId, onSelect }: TimelineBranchListProps) {
  return (
    <section className="page-card">
      <h3>分支列表</h3>
      <ul className="session-list">
        {branches.map((branch) => (
          <li className="branch-item" key={branch.id}>
            <button
              className={branch.id === selectedBranchId ? "branch-button active" : "branch-button"}
              onClick={() => onSelect?.(branch)}
              type="button"
            >
              切换到 branch {branch.branch_name}
            </button>
            <span>
              tick {branch.current_tick}
              {branch.is_main ? " / main" : ""}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
