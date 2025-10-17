// Lightweight Overpass API checker for protected or reserve areas near a coordinate
// Returns whether the point intersects any protected/nature reserve boundaries and their names

export interface ProtectedAreaCheckResult {
  isProtected: boolean
  names: string[]
}

// Overpass QL: search for relations/ways around point with tags indicating protection
export async function checkProtectedArea(latitude: number, longitude: number): Promise<ProtectedAreaCheckResult> {
  // Validate inputs
  if (!isFinite(latitude) || !isFinite(longitude)) {
    return { isProtected: false, names: [] }
  }

  // Primary query: containment-based using is_in and area lookups so very large parks are detected
  const containmentQuery = `
    [out:json][timeout:25];
    node(${latitude},${longitude});
    is_in;
    area._;
    (
      area["boundary"="protected_area"];
      area["leisure"="nature_reserve"];
      area["boundary"="national_park"];
    );
    out tags;
  `

  try {
    const resp = await fetch("https://overpass-api.de/api/interpreter", {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      body: containmentQuery,
    })

    if (!resp.ok) {
      return { isProtected: false, names: [] }
    }

    const data = await resp.json()
    const elements = Array.isArray(data?.elements) ? data.elements : []
    const names: string[] = []

    for (const el of elements) {
      const n = el?.tags?.name || el?.tags?.["name:en"] || el?.tags?.["protect_title"]
      if (typeof n === "string" && n.trim()) {
        names.push(n.trim())
      }
    }

    // Remove duplicates
    let unique = Array.from(new Set(names))

    // Fallback: if containment did not match anything, try a larger-radius proximity search
    if (unique.length === 0) {
      const radiusMeters = 15000 // 15 km to catch large polygons by boundary proximity
      const aroundQuery = `
        [out:json][timeout:25];
        (
          relation["boundary"="protected_area"](around:${radiusMeters},${latitude},${longitude});
          way["boundary"="protected_area"](around:${radiusMeters},${latitude},${longitude});
          relation["leisure"="nature_reserve"](around:${radiusMeters},${latitude},${longitude});
          way["leisure"="nature_reserve"](around:${radiusMeters},${latitude},${longitude});
          relation["boundary"="national_park"](around:${radiusMeters},${latitude},${longitude});
          way["boundary"="national_park"](around:${radiusMeters},${latitude},${longitude});
        );
        out tags;
      `
      try {
        const resp2 = await fetch("https://overpass-api.de/api/interpreter", {
          method: "POST",
          headers: { "Content-Type": "text/plain;charset=UTF-8" },
          body: aroundQuery,
        })
        if (resp2.ok) {
          const data2 = await resp2.json()
          const elements2 = Array.isArray(data2?.elements) ? data2.elements : []
          for (const el of elements2) {
            const n2 = el?.tags?.name || el?.tags?.["name:en"] || el?.tags?.["protect_title"]
            if (typeof n2 === "string" && n2.trim()) {
              names.push(n2.trim())
            }
          }
          unique = Array.from(new Set(names))
        }
      } catch (_e) {
        // ignore
      }
    }

    return { isProtected: unique.length > 0, names: unique }
  } catch (_err) {
    return { isProtected: false, names: [] }
  }
}

export function buildProtectedDisclaimer(names: string[]): string {
  const named = names.length
    ? ` (e.g., ${names.slice(0, 3).join(", ")}${names.length > 3 ? ", ..." : ""})`
    : ""
  return (
    "The selected coordinates appear to be within or near a protected/" +
    "reserve area" + named + ".\n\n" +
    "Analyses are for informational purposes only and do not constitute legal, " +
    "environmental, or permitting advice. Proceeding may require additional due diligence.\n\n" +
    "Do you still want to continue with the analysis?"
  )
}
