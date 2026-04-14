/**
 * Razorpay Script Loader (PRODUCTION-GRADE)
 * Ensures Razorpay checkout script is loaded before payment execution
 */

let razorpayScriptLoaded = false;
let razorpayScriptLoading = false;
let razorpayLoadPromise = null;

export const loadRazorpayScript = () => {
    // Return existing promise if already loading
    if (razorpayLoadPromise) {
        return razorpayLoadPromise;
    }

    // Return resolved promise if already loaded
    if (razorpayScriptLoaded && window.Razorpay) {
        return Promise.resolve(true);
    }

    // Create new loading promise
    razorpayLoadPromise = new Promise((resolve, reject) => {
        // Check if script already exists
        const existingScript = document.querySelector('script[src="https://checkout.razorpay.com/v1/checkout.js"]');
        
        if (existingScript) {
            if (window.Razorpay) {
                razorpayScriptLoaded = true;
                resolve(true);
                return;
            }
            
            // Script exists but not loaded yet, wait for it
            existingScript.addEventListener('load', () => {
                razorpayScriptLoaded = true;
                resolve(true);
            });
            
            existingScript.addEventListener('error', () => {
                reject(new Error('Failed to load Razorpay script'));
            });
            
            return;
        }

        // Create and inject script
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;

        script.onload = () => {
            razorpayScriptLoaded = true;
            razorpayScriptLoading = false;
            console.log('✅ Razorpay script loaded successfully');
            resolve(true);
        };

        script.onerror = () => {
            razorpayScriptLoading = false;
            razorpayLoadPromise = null;
            console.error('❌ Failed to load Razorpay script');
            reject(new Error('Failed to load Razorpay checkout script. Please check your internet connection.'));
        };

        razorpayScriptLoading = true;
        document.body.appendChild(script);
    });

    return razorpayLoadPromise;
};

export const isRazorpayLoaded = () => {
    return razorpayScriptLoaded && window.Razorpay;
};
