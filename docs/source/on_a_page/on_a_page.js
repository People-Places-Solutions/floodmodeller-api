fetch('on_a_page_snippets.json')
    .then(response => response.json())
    .then(snippets => {
        const codeGrid = document.getElementById('codeGrid');
        const modal = document.getElementById('code-modal');
        const modalCode = document.getElementById('modal-code');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.querySelector('.modal-content');

        snippets.forEach(snippet => {
            const block = document.createElement('div');
            block.className = `code-block ${snippet.size || 's'}`;

            block.innerHTML = `
        <div class="code-title">${snippet.title}</div>
        <pre><code class="language-python">${Prism.util.encode(snippet.code)}</code></pre>
      `;

            codeGrid.appendChild(block);

            // Add modal click behavior
            block.addEventListener('click', () => {
                modalCode.textContent = snippet.code;
                modalTitle.textContent = snippet.title;
                modal.style.display = 'flex';

                if (window.Prism) {
                    Prism.highlightElement(modalCode);
                }
            });
        });

        // Highlight all newly inserted code blocks
        Prism.highlightAll();

        // Wait for DOM/layout to settle before checking for overflow
        setTimeout(updateCodeBlockGradients, 0);
    })
    .catch(error => {
        console.error('Failed to load code snippets:', error);
    });

// Function to add .is-clipped class only to overflowing code blocks
function updateCodeBlockGradients() {
  document.querySelectorAll('.code-block').forEach(block => {
    // wait for any layout recalculations
    requestAnimationFrame(() => {
      const pre = block.querySelector('pre');

      if (!pre) return;

      const preScrollHeight = pre.scrollHeight;
      const preClientHeight = pre.clientHeight;

      if (preScrollHeight > preClientHeight) {
        block.classList.add('is-clipped');
      } else {
        block.classList.remove('is-clipped');
      }

      // Debug log (optional)
      console.log({
        title: block.querySelector('.code-title')?.textContent,
        preScrollHeight,
        preClientHeight,
        clipped: preScrollHeight > preClientHeight
      });
    });
  });
}

// Re-check on window resize
window.addEventListener('resize', updateCodeBlockGradients);

// Modal close when clicking outside content
const modal = document.getElementById('code-modal');
const modalContent = document.querySelector('.modal-content');

modal.addEventListener('click', (event) => {
    if (!modalContent.contains(event.target)) {
        modal.style.display = 'none';
    }
});

// Copy-to-clipboard from modal
document.querySelector('.copy-button').addEventListener('click', () => {
    const codeText = document.getElementById('modal-code').textContent;
    const icon = document.querySelector('.copy-button img');

    navigator.clipboard.writeText(codeText).then(() => {
        const originalSrc = icon.src;
        icon.src = "_static/tick-icon.png";
        setTimeout(() => icon.src = originalSrc, 1500);
    }).catch(err => {
        console.error('Copy failed', err);
    });
});
