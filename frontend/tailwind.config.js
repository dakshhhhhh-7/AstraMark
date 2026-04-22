/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)',
  			xl: 'calc(var(--radius) + 4px)',
  			'2xl': 'calc(var(--radius) + 8px)'
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			success: {
  				DEFAULT: 'hsl(var(--success))',
  				foreground: 'hsl(var(--success-foreground))'
  			},
  			warning: {
  				DEFAULT: 'hsl(var(--warning))',
  				foreground: 'hsl(var(--warning-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			// Premium color palette
  			indigo: {
  				DEFAULT: '#6366F1',
  				50: '#EEEEFF',
  				100: '#E0E1FF',
  				200: '#C7C9FE',
  				300: '#A5A7FC',
  				400: '#8184F8',
  				500: '#6366F1',
  				600: '#4F46E5',
  				700: '#4338CA',
  				800: '#3730A3',
  				900: '#312E81'
  			},
  			purple: {
  				DEFAULT: '#A855F7',
  				50: '#FAF5FF',
  				100: '#F3E8FF',
  				200: '#E9D5FF',
  				300: '#D8B4FE',
  				400: '#C084FC',
  				500: '#A855F7',
  				600: '#9333EA',
  				700: '#7E22CE',
  				800: '#6B21A8',
  				900: '#581C87'
  			},
  			cyan: {
  				DEFAULT: '#22D3EE',
  				50: '#ECFEFF',
  				100: '#CFFAFE',
  				200: '#A5F3FC',
  				300: '#67E8F9',
  				400: '#22D3EE',
  				500: '#06B6D4',
  				600: '#0891B2',
  				700: '#0E7490',
  				800: '#155E75',
  				900: '#164E63'
  			}
  		},
  		backgroundImage: {
  			'gradient-primary': 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
  			'gradient-accent': 'linear-gradient(135deg, #22D3EE 0%, #6366F1 100%)',
  			'gradient-success': 'linear-gradient(135deg, #10B981 0%, #22D3EE 100%)',
  			'gradient-radial': 'radial-gradient(circle, var(--tw-gradient-stops))'
  		},
  		boxShadow: {
  			'premium': '0 20px 50px rgba(0, 0, 0, 0.5), 0 10px 20px rgba(0, 0, 0, 0.3)',
  			'neon': '0 0 20px rgba(34, 211, 238, 0.5), 0 0 40px rgba(34, 211, 238, 0.3)',
  			'glow': '0 0 30px rgba(99, 102, 241, 0.5), 0 0 60px rgba(168, 85, 247, 0.3)'
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			},
  			'fade-in': {
  				from: {
  					opacity: '0'
  				},
  				to: {
  					opacity: '1'
  				}
  			},
  			'slide-up': {
  				from: {
  					transform: 'translateY(20px)',
  					opacity: '0'
  				},
  				to: {
  					transform: 'translateY(0)',
  					opacity: '1'
  				}
  			},
  			'pulse-glow': {
  				'0%, 100%': {
  					boxShadow: '0 0 20px rgba(34, 211, 238, 0.5)'
  				},
  				'50%': {
  					boxShadow: '0 0 40px rgba(34, 211, 238, 0.8)'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out',
  			'fade-in': 'fade-in 0.3s ease-out',
  			'slide-up': 'slide-up 0.4s ease-out',
  			'pulse-glow': 'pulse-glow 2s ease-in-out infinite'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
};