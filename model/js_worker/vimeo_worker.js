const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const fs = require('fs');

// Args: node vimeo_worker.js <name> <email> <password> <proxy|null> <is_mobile>
const args = process.argv.slice(2);
const NAME = args[0];
const EMAIL = args[1];
const PASSWORD = args[2];
const PROXY = args[3] !== 'None' ? args[3] : null;
const IS_MOBILE = args[4] === 'True';

(async () => {
    const launchOptions = {
        headless: false, // Visible for now, user likes to see
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-position=0,0',
            '--ignore-certifcate-errors',
            '--ignore-certifcate-errors-spki-list',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--log-level=3', // Fatal only
            '--disable-logging',
            '--disable-features=IsolateOrigins,site-per-process', // Helps with some iframe issues
        ],
        ignoreDefaultArgs: ['--enable-automation'],
        defaultViewport: null
    };

    if (PROXY) {
        // PROXY Format: IP:PORT or IP:PORT:USER:PASS
        const parts = PROXY.split(':');
        if (parts.length >= 2) {
            launchOptions.args.push(`--proxy-server=${parts[0]}:${parts[1]}`);
        }
    }

    if (IS_MOBILE) {
        // Mobile emulation arguments handled via page.emulate later, 
        // but let's set window size for launch
        launchOptions.args.push('--window-size=390,844');
    } else {
        launchOptions.args.push('--window-size=1920,1080');
    }

    let browser;
    try {
        browser = await puppeteer.launch(launchOptions);
        const page = await browser.newPage();

        // proxy auth if needed
        if (PROXY) {
            const parts = PROXY.split(':');
            if (parts.length === 4) {
                await page.authenticate({
                    username: parts[2],
                    password: parts[3]
                });
            }
        }

        if (IS_MOBILE) {
            // Emulate iPhone 12 Pro
            const device = puppeteer.devices['iPhone 12 Pro'];
            await page.emulate(device);
        } else {
            // Random Desktop UA
            const ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36";
            await page.setUserAgent(ua);
            await page.setViewport({ width: 1920, height: 1080 });
        }

        // --- 1. IP CHECK ---
        console.log('[NODE] 🔎 Checking IP...');
        try {
            await page.goto('https://api64.ipify.org?format=json', { waitUntil: 'domcontentloaded', timeout: 15000 });
            const content = await page.evaluate(() => document.body.innerText);
            console.log(`[NODE] 🌍 IP: ${content}`);
        } catch (e) {
            console.log(`[NODE] ⚠️ IP Check Failed: ${e.message}`);
        }

        // --- 2. NAVIGATE VIMEO ---
        console.log('[NODE] Navigating to Vimeo...');
        await page.goto('https://vimeo.com/join', { waitUntil: 'networkidle2', timeout: 60000 });

        // --- 3. CLOUDFLARE/CAPTCHA CHECK ---
        // Puppeteer Stealth usually handles the JS challenge automatically.
        // We just wait a bit to be sure.
        await new Promise(r => setTimeout(r, 5000));

        // Check for "Verify to continue" loop
        let retries = 0;
        while (retries < 15) {
            const title = await page.title();
            const body = await page.evaluate(() => document.body.innerText);
            
            if (body.includes('Verify to continue') || title.includes('Just a moment')) {
                console.log(`[NODE] ⚠️ Cloudflare Detected. Waiting... (${retries}/15)`);
                
                // Try to click turnstile if visible
                try {
                     const frame = page.frames().find(f => f.url().includes('turnstile') || f.url().includes('challenge'));
                     if (frame) {
                         await frame.click('input[type="checkbox"]').catch(() => {});
                     }
                     // Click shadow dom if any
                     await page.evaluate(() => {
                         const host = document.querySelector('.cf-turnstile');
                         if(host) host.click();
                     });
                } catch(e) {}
                
                await new Promise(r => setTimeout(r, 5000));
                retries++;
            } else {
                break;
            }
        }

        // --- 4. FILL FORM ---
        console.log('[NODE] Filling Form...');
        // Wait for inputs
        await page.waitForSelector('input[name="name"]', { timeout: 30000 });
        
        await page.type('input[name="name"]', NAME, { delay: 100 });
        await page.type('input[name="email"]', EMAIL, { delay: 100 });
        await page.type('input[type="password"]', PASSWORD, { delay: 100 });
        
        await new Promise(r => setTimeout(r, 1000));
        
        // Click Join
        // Try multiple selectors
        const btnSelector = 'button[type="submit"], .join-button';
        await page.waitForSelector(btnSelector);
        await page.click(btnSelector);
        
        console.log('[NODE] Clicked Join. Waiting for result...');
        await new Promise(r => setTimeout(r, 5000));

        // Check URL or Content
        // Validation loop
        const endTime = Date.now() + 60000; // 60s wait
        while (Date.now() < endTime) {
            const url = page.url();
            if (!url.includes('join') && !url.includes('log_in')) {
                console.log('[NODE] ✅ SUCCESS: Created Account!');
                
                // Save cookies?
                const cookies = await page.cookies();
                fs.writeFileSync('vimeo_node_cookies.json', JSON.stringify(cookies));
                
                // Save Account
                fs.appendFileSync('../../vimeo_accounts.txt', `${EMAIL}|${PASSWORD}|${NAME}\n`);
                
                break;
            }
            // Check errors
            const error = await page.evaluate(() => {
                const el = document.querySelector('.error_msg, [class*="error"]');
                return el ? el.innerText : null;
            });
            if (error) {
                console.log(`[NODE] ❌ Error: ${error}`);
            }
            
            await new Promise(r => setTimeout(r, 2000));
        }

    } catch (err) {
        console.error(`[NODE] ❌ CRITICAL ERROR: ${err.message}`);
    } finally {
        if (browser) await browser.close();
    }
})();
