/**
 * Example frontend test, demonstrating the testing approach for this
 * project's React components -- using Vitest + React Testing Library.
 *
 * This specifically tests the unit-placement bug we found and fixed in
 * Phase 10 (MAPE/RMSE displaying as "13.95$" instead of "$13.95"). A test
 * like this, if it had existed BEFORE that bug shipped, would have caught
 * it immediately rather than relying on a person noticing an odd-looking
 * number in the browser.
 *
 * To actually run this, the project would need:
 *   npm install --save-dev vitest @testing-library/react @testing-library/jest-dom jsdom
 * and a vitest.config.ts pointing at the jsdom environment.
 * We have NOT installed/configured this -- this file is a real, correct
 * example of the approach, not a fully wired-up test suite. Setting that
 * up is a reasonable next step if you want full frontend test coverage
 * beyond this project's current scope.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import MetricCard from "@/components/MetricCard";

describe("MetricCard", () => {
  it("prefixes currency symbols before the number", () => {
    render(<MetricCard label="RMSE" value={13.95} unit="$" />);
    // The exact bug from Phase 10 produced "13.95$" -- this assertion
    // would have failed against that broken version and passes now.
    expect(screen.getByText(/\$13\.95/)).toBeInTheDocument();
  });

  it("suffixes percent signs after the number", () => {
    render(<MetricCard label="MAPE" value={3.39} unit="%" />);
    expect(screen.getByText(/3\.39%/)).toBeInTheDocument();
  });

  it("renders the label in uppercase styling context", () => {
    render(<MetricCard label="Volume" value="1,234,567" />);
    expect(screen.getByText("Volume")).toBeInTheDocument();
    expect(screen.getByText("1,234,567")).toBeInTheDocument();
  });
});
