(() => {
  const report = document.querySelector("#report-content");
  const search = document.querySelector("#site-search");
  const searchStatus = document.querySelector("#search-status");
  const toc = document.querySelector("#table-of-contents");

  document.querySelectorAll("table").forEach((table) => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-scroll";
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  const programHeadings = [...report.querySelectorAll("h2")].filter((heading) =>
    /^(?:\(\d+\)\s+)?Program\s+\d+:/.test(heading.textContent.trim())
  );

  const cards = programHeadings.map((heading) => {
    const details = document.createElement("details");
    details.className = "program-card";
    details.id = heading.id || heading.closest("section")?.id || heading.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-");
    const summary = document.createElement("summary");
    summary.textContent = heading.textContent;
    const body = document.createElement("div");
    body.className = "program-body";
    heading.parentNode.insertBefore(details, heading);
    details.append(summary, body);
    let node = heading.nextSibling;
    heading.remove();
    while (node && !(node.nodeType === 1 && (node.matches("h1, h2") || node.querySelector?.("h1, h2")))) {
      const next = node.nextSibling;
      body.appendChild(node);
      node = next;
    }
    return details;
  });

  const headings = [...report.querySelectorAll("h1, h2")].filter((heading) =>
    heading.id || heading.closest("section")?.id
  );
  headings.forEach((heading) => {
    const link = document.createElement("a");
    link.href = `#${heading.id || heading.closest("section").id}`;
    link.textContent = heading.textContent;
    link.className = heading.tagName === "H1" ? "toc-h1" : "toc-h2";
    toc.appendChild(link);
  });

  const tables = [...document.querySelectorAll("table")];
  const summaryTables = tables.filter((table) => {
    const header = table.querySelector("th");
    return header && header.textContent.trim() === "program ID";
  });
  summaryTables.forEach((summaryTable) => {
    const tools = document.createElement("div");
    tools.className = "table-tools";
    const filter = document.createElement("input");
    filter.className = "table-filter";
    filter.type = "search";
    filter.placeholder = "Filter summary table";
    filter.setAttribute("aria-label", "Filter summary table");
    const count = document.createElement("span");
    count.className = "table-count";
    tools.append(filter, count);
    summaryTable.closest(".table-scroll").before(tools);
    const rows = [...summaryTable.querySelectorAll("tbody tr")];
    const applyFilter = () => {
      const query = filter.value.trim().toLowerCase();
      let visible = 0;
      rows.forEach((row) => {
        const match = !query || row.textContent.toLowerCase().includes(query);
        row.hidden = !match;
        if (match) visible += 1;
      });
      count.textContent = `${visible} rows`;
    };
    filter.addEventListener("input", applyFilter);
    applyFilter();
  });

  const applySearch = () => {
    const query = search.value.trim().toLowerCase();
    const programIdQuery = /^\d+$/.test(query);
    let visible = 0;
    cards.forEach((card) => {
      const summaryText = card.querySelector("summary").textContent.toLowerCase();
      const match = !query || (programIdQuery ? summaryText.includes(`program ${query}:`) : card.textContent.toLowerCase().includes(query));
      card.classList.toggle("program-hidden", !match);
      if (match) {
        visible += 1;
        if (query) card.open = true;
      }
    });
    searchStatus.textContent = `${visible} programs`;
  };
  search.addEventListener("input", applySearch);
  applySearch();
})();
