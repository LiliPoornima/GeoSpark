import React from "react";
import { ProtectedAreaCheckResult } from "../services/protectedAreas";

interface Props {
  result: ProtectedAreaCheckResult;
  onProceed: () => void;
  onCancel: () => void;
}

export const ProtectedAreaModal: React.FC<Props> = ({ result, onProceed, onCancel }) => {
  if (!result.isProtected) return null;

  const displayedNames = result.names.slice(0, 3).join(", ");
  const more = result.names.length > 3 ? ", ..." : "";

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          background: "white",
          padding: "2rem",
          borderRadius: "12px",
          maxWidth: "500px",
          textAlign: "center",
          boxShadow: "0 0 20px rgba(0,0,0,0.3)",
        }}
      >
        <h2 style={{ color: "red", fontWeight: "bold", marginBottom: "1rem" }}>
          ⚠️ Protected Area Alert!
        </h2>
        <p style={{ fontSize: "1rem", marginBottom: "1rem" }}>
          The selected coordinates appear to be within or near a protected/reserve area
          {displayedNames ? ` (e.g., ${displayedNames}${more})` : ""}.
        </p>
        <p style={{ fontSize: "0.9rem", color: "#555", marginBottom: "1.5rem" }}>
          Analyses are for informational purposes only and do not constitute legal, environmental, or permitting advice.
        </p>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <button
            onClick={onCancel}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: "1px solid #ccc",
              background: "#f0f0f0",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
          <button
            onClick={onProceed}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: "none",
              background: "red",
              color: "white",
              cursor: "pointer",
            }}
          >
            Proceed Anyway
          </button>
        </div>
      </div>
    </div>
  );
};
