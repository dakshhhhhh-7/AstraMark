/**
 * Razorpay Payment Handler (PRODUCTION-GRADE)
 * Fail-proof payment initialization with comprehensive error handling
 */

import apiClient, { getAccessToken } from '@/utils/apiClient';
import { loadRazorpayScript } from './razorpayLoader';

/**
 * Initialize Razorpay payment (FAIL-PROOF)
 * @param {string} planId - Subscription plan ID
 * @param {Function} onSuccess - Success callback
 * @param {Function} onFailure - Failure callback
 */
export const initiateRazorpayPayment = async (planId, onSuccess, onFailure) => {
    try {
        console.log('🚀 Starting Razorpay payment flow for plan:', planId);

        // STEP 1: Validate authentication
        const token = getAccessToken();
        console.log('🔐 Token check:', token ? 'Token exists in memory' : 'No token found');
        
        if (!token) {
            throw new Error('AUTHENTICATION_REQUIRED: Please log in to continue');
        }

        // STEP 2: Load Razorpay script
        console.log('📦 Loading Razorpay checkout script...');
        try {
            await loadRazorpayScript();
            console.log('✅ Razorpay script loaded');
        } catch (scriptError) {
            throw new Error('SCRIPT_LOAD_FAILED: Unable to load payment gateway. Please check your internet connection and try again.');
        }

        // STEP 3: Verify Razorpay object exists
        if (!window.Razorpay) {
            throw new Error('RAZORPAY_UNAVAILABLE: Payment gateway not available. Please refresh the page and try again.');
        }

        // STEP 4: Create order on backend (using centralized API client)
        console.log('🔐 Creating payment order on server...');
        let orderResponse;
        try {
            orderResponse = await apiClient.post('/api/payments/razorpay/create-order', {
                plan_id: planId
            });
        } catch (apiError) {
            console.error('❌ Order creation failed:', apiError);
            
            if (apiError.response) {
                // Server responded with error
                const status = apiError.response.status;
                const message = apiError.response.data?.detail || 'Server error';
                
                if (status === 401) {
                    throw new Error('AUTHENTICATION_EXPIRED: Your session has expired. Please log in again.');
                } else if (status === 503) {
                    throw new Error('SERVICE_UNAVAILABLE: Payment service is temporarily unavailable. Please try again later.');
                } else {
                    throw new Error(`SERVER_ERROR: ${message}`);
                }
            } else if (apiError.request) {
                // Request made but no response
                throw new Error('NETWORK_ERROR: Unable to connect to server. Please check your internet connection.');
            } else {
                throw new Error(`REQUEST_FAILED: ${apiError.message}`);
            }
        }

        // STEP 5: Validate order response
        console.log('📋 Order response:', orderResponse.data);
        
        if (!orderResponse.data || !orderResponse.data.success) {
            throw new Error('INVALID_RESPONSE: Server returned invalid response');
        }

        const order = orderResponse.data.order;
        
        if (!order || !order.order_id) {
            console.error('❌ Invalid order object:', order);
            throw new Error('INVALID_ORDER: Payment order is missing required information');
        }

        if (!order.key_id) {
            throw new Error('MISSING_KEY: Payment gateway configuration error');
        }

        console.log('✅ Order created successfully:', order.order_id);

        // STEP 6: Configure Razorpay options
        const razorpayOptions = {
            key: order.key_id,
            amount: order.amount,
            currency: order.currency,
            name: 'AstraMark',
            description: `${order.plan_id.toUpperCase()} Plan Subscription`,
            order_id: order.order_id,
            prefill: {
                name: order.user_name,
                email: order.user_email
            },
            theme: {
                color: '#6366f1'
            },
            modal: {
                ondismiss: function() {
                    console.log('⚠️ Payment modal closed by user');
                    if (onFailure) {
                        onFailure({
                            code: 'PAYMENT_CANCELLED',
                            message: 'Payment was cancelled'
                        });
                    }
                }
            },
            handler: async function(response) {
                console.log('✅ Payment successful, verifying...', response);
                
                try {
                    // STEP 7: Verify payment on backend (using centralized API client)
                    const verifyResponse = await apiClient.post('/api/payments/razorpay/verify', {
                        order_id: response.razorpay_order_id,
                        payment_id: response.razorpay_payment_id,
                        signature: response.razorpay_signature
                    });

                    console.log('✅ Payment verified successfully');
                    
                    if (onSuccess) {
                        onSuccess(verifyResponse.data);
                    }
                } catch (verifyError) {
                    console.error('❌ Payment verification failed:', verifyError);
                    
                    if (onFailure) {
                        onFailure({
                            code: 'VERIFICATION_FAILED',
                            message: 'Payment verification failed. Please contact support.',
                            error: verifyError
                        });
                    }
                }
            }
        };

        // STEP 8: Open Razorpay checkout
        console.log('💳 Opening Razorpay checkout...');
        const razorpayInstance = new window.Razorpay(razorpayOptions);
        
        razorpayInstance.on('payment.failed', function(response) {
            console.error('❌ Payment failed:', response.error);
            
            if (onFailure) {
                onFailure({
                    code: 'PAYMENT_FAILED',
                    message: response.error.description || 'Payment failed',
                    reason: response.error.reason,
                    error: response.error
                });
            }
        });

        razorpayInstance.open();
        console.log('✅ Razorpay checkout opened successfully');

    } catch (error) {
        console.error('❌ Payment initialization failed:', error);
        
        if (onFailure) {
            onFailure({
                code: error.message.split(':')[0] || 'UNKNOWN_ERROR',
                message: error.message.split(':')[1]?.trim() || error.message,
                error: error
            });
        }
    }
};
