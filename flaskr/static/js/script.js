document.addEventListener('DOMContentLoaded', function() {
    // Accessibility toggle functionality
    const accessibilityToggle = document.getElementById('accessibility-toggle');
    
    // Check if the a11y-text element exists, if not create it
    if (!accessibilityToggle.querySelector('.a11y-text')) {
        const textElement = document.createElement('span');
        textElement.className = 'a11y-text';
        textElement.textContent = 'Standard';
        accessibilityToggle.appendChild(textElement);
    }
    
    // Check if accessibility mode was previously enabled
    const accessibilityMode = localStorage.getItem('accessibilityMode') === 'true';
    
    // Apply accessibility mode if it was enabled
    if (accessibilityMode) {
        toggleAccessibilityMode();
    }
    
    accessibilityToggle.addEventListener('click', function() {
        toggleAccessibilityMode();
        
        // Save preference to localStorage
        const currentMode = localStorage.getItem('accessibilityMode') === 'true';
        localStorage.setItem('accessibilityMode', (!currentMode).toString());
    });
    
    function toggleAccessibilityMode() {
        // Check if we're currently in accessibility mode
        const isCurrentlyAccessible = document.body.classList.contains('accessibility-mode');
        
        if (!isCurrentlyAccessible) {
            // ENABLE ACCESSIBILITY MODE
            document.body.classList.add('accessibility-mode');
            
            // 1. Disable external stylesheets
            const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
            stylesheets.forEach(sheet => {
                sheet.disabled = true;
            });
            
            // 2. Disable all <style> elements
            const styles = document.querySelectorAll('style');
            styles.forEach(style => {
                style.disabled = true;
                // Also store them for later re-enabling
                style.setAttribute('data-a11y-disabled', 'true');
            });
            
            // 3. Save and preserve specific inline styles (charts) but remove others
            document.querySelectorAll('[style]').forEach(el => {
                // Save all original styles
                el.setAttribute('data-original-style', el.getAttribute('style'));
            });

            // 4. Apply basic accessibility styles
            const accessibilityStyles = document.createElement('style');
            accessibilityStyles.id = 'accessibility-styles';
            accessibilityStyles.textContent = `
                body, html {
                    font-family: Arial, sans-serif !important;
                    font-size: 16px !important;
                    line-height: 1.5 !important;
                    color: #000 !important;
                    background-color: #fff !important;
                    margin: 20px !important;
                }
                a { 
                    color: blue !important; 
                    text-decoration: underline !important;
                    font-weight: bold !important;
                }
                a:visited { color: purple !important; }
                button, input, select { 
                    border: 1px solid #333 !important;
                    padding: 5px !important;
                    margin: 5px !important;
                    background: #f1f1f1 !important;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #000 !important;
                    margin-top: 1em !important;
                    margin-bottom: 0.5em !important;
                }
                nav, header, footer, .accessibility-btn {
                    border: 1px solid #333 !important;
                    padding: 10px !important;
                    margin: 5px 0 !important;
                }
                img { display: none !important; }
                .alt-text { 
                    display: block !important;
                    padding: 5px !important;
                    margin: 5px 0 !important;
                    border: 1px dashed #333 !important;
                }
                /* Preserve chart containers */
                canvas, .chart-container {
                    max-width: 100% !important;
                    max-height: 200px !important;
                    box-sizing: border-box !important;
                }
                /* Add descriptions for charts */
                .chart-description {
                    border: 1px dashed #333 !important;
                    padding: 10px !important;
                    margin: 10px 0 !important;
                    background-color: #f9f9f9 !important;
                }
                .chart-container, .progress-container, .progress-text {
                visibility: hidden;}
            `;
            document.head.appendChild(accessibilityStyles);
            
            // 5. Replace images with alt text
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                // Don't process already processed images
                if (img.getAttribute('data-a11y-processed') === 'true') return;
                
                // Save original state and hide image
                img.setAttribute('data-original-src', img.src);
                img.setAttribute('data-a11y-processed', 'true');
                
                // Create alt text element if alt exists
                if (img.alt) {
                    const altText = document.createElement('span');
                    altText.className = 'alt-text';
                    altText.textContent = `[Image: ${img.alt}]`;
                    img.parentNode.insertBefore(altText, img.nextSibling);
                }
            });
            
            // 6. Add descriptions to charts for better accessibility
            document.querySelectorAll('canvas').forEach(canvas => {
                // Check if it's likely a chart
                if (canvas.id.includes('chart') || 
                    canvas.classList.contains('chart-js') || 
                    canvas.hasAttribute('data-chart-type') ||
                    canvas.parentElement && canvas.parentElement.classList.contains('chart-container')) {
                    
                    // Check if we already added a description
                    if (!canvas.nextElementSibling || !canvas.nextElementSibling.classList.contains('chart-description')) {
                        const chartTitle = canvas.getAttribute('aria-label') || 
                                           canvas.getAttribute('data-chart-title') || 
                                           'Chart';
                        
                        const description = document.createElement('div');
                        description.className = 'chart-description';
                        description.innerHTML = `<strong>Chart description:</strong> ${chartTitle}`;
                        
                        if (canvas.parentElement && canvas.parentElement.classList.contains('chart-container')) {
                            canvas.parentElement.insertBefore(description, canvas.nextSibling);
                        } else {
                            canvas.parentNode.insertBefore(description, canvas.nextSibling);
                        }
                    }
                }
            });
        } else {
            // DISABLE ACCESSIBILITY MODE
            document.body.classList.remove('accessibility-mode');
            
            // 1. Re-enable external stylesheets
            const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
            stylesheets.forEach(sheet => {
                sheet.disabled = false;
            });
            
            // 2. Re-enable all <style> elements
            const styles = document.querySelectorAll('style[data-a11y-disabled="true"]');
            styles.forEach(style => {
                style.disabled = false;
                style.removeAttribute('data-a11y-disabled');
            });
            
            // 3. Remove our accessibility style
            const accessibilityStyles = document.getElementById('accessibility-styles');
            if (accessibilityStyles) {
                accessibilityStyles.remove();
            }
            
            // 4. Restore all inline styles
            document.querySelectorAll('[data-original-style]').forEach(el => {
                el.setAttribute('style', el.getAttribute('data-original-style'));
                el.removeAttribute('data-original-style');
            });
            
            // 5. Restore images and remove alt text
            const images = document.querySelectorAll('img[data-a11y-processed="true"]');
            images.forEach(img => {
                img.removeAttribute('data-a11y-processed');
            });
            
            // 6. Remove added descriptions and alt texts
            const altTexts = document.querySelectorAll('.alt-text, .chart-description');
            altTexts.forEach(el => el.remove());
        }
        
        // Announce mode change for screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.style.position = 'absolute';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = 'Accessibility mode ' + 
            (document.body.classList.contains('accessibility-mode') ? 'enabled' : 'disabled');
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
});
