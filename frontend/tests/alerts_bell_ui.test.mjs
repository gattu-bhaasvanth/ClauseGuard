import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Alerts/Bell UI Popover & Interaction Tests", () => {
  const headerPath = path.join(frontendRoot, "src/components/layout/DashboardHeader.tsx");

  it("1. DashboardHeader renders interactive bell button with proper accessibility attributes", () => {
    assert.ok(fs.existsSync(headerPath), "DashboardHeader.tsx must exist");
    const content = fs.readFileSync(headerPath, "utf-8");

    // Must have bell button with ID and aria attributes
    assert.ok(content.includes('id="alerts-bell-button"'), "Bell button must have id alerts-bell-button");
    assert.ok(content.includes('aria-label="Notifications"'), "Bell button must have aria-label Notifications");
    assert.ok(content.includes('aria-expanded={alertsOpen}'), "Bell button must bind aria-expanded to open state");
    assert.ok(content.includes('aria-haspopup="true"'), "Bell button must specify aria-haspopup");
    assert.ok(content.includes("onClick={() => setAlertsOpen"), "Bell button must have an active onClick toggle handler");
  });

  it("2. Alerts dropdown panel is conditionally rendered and contains dialog role and proper labels", () => {
    const content = fs.readFileSync(headerPath, "utf-8");

    assert.ok(content.includes('id="alerts-dropdown-panel"'), "Dropdown panel must have id alerts-dropdown-panel");
    assert.ok(content.includes('role="dialog"'), "Dropdown panel must have role dialog");
    assert.ok(content.includes('aria-label="Alerts & Notifications"'), "Dropdown panel must have descriptive aria-label");
    assert.ok(content.includes("Alerts & Notifications"), "Dropdown header must display Alerts & Notifications title");
  });

  it("3. Displays truthful 'No new alerts' empty state without fabricated data", () => {
    const content = fs.readFileSync(headerPath, "utf-8");

    assert.ok(content.includes("No new alerts"), "Must render 'No new alerts' heading in empty state");
    assert.ok(content.includes("All property transaction monitors are clear"), "Must describe peaceful audit state");
    // Verify no hardcoded demo names in alert messages
    assert.ok(!content.includes("SkyView"), "Alerts header must not hardcode SkyView");
    assert.ok(!content.includes("Maple Heights"), "Alerts header must not hardcode Maple Heights");
    assert.ok(!content.includes("Harbor Crest"), "Alerts header must not hardcode Harbor Crest");
  });

  it("4. Supports real alert items with severity badges and timestamps when provided", () => {
    const content = fs.readFileSync(headerPath, "utf-8");

    assert.ok(content.includes("alerts.map"), "Must map over real alert items when present");
    assert.ok(content.includes("alert.severity"), "Must render alert severity badges");
    assert.ok(content.includes("alert.title"), "Must render alert title");
    assert.ok(content.includes("alert.description"), "Must render alert description");
  });

  it("5. Implements click-outside and Escape key handlers to dismiss the popover", () => {
    const content = fs.readFileSync(headerPath, "utf-8");

    assert.ok(content.includes("handleClickOutside"), "Must implement handleClickOutside listener");
    assert.ok(content.includes('event.key === "Escape"'), "Must handle Escape key to close popover");
    assert.ok(content.includes("removeEventListener"), "Must clean up event listeners on unmount or close");
    assert.ok(content.includes('aria-label="Close alerts"'), "Must provide explicit close button with aria-label");
  });
});
