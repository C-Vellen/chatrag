const colors = require('tailwindcss/colors')

module.exports = {
    content: [
        '../templates/**/*.html',
        
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
        '../../../**/templates/**/*.html',
        '../src/**/*.css',
        '../src/**/*.js',
        '../src/**/*.py',
    ],
    theme: {
        extend: {
             /* custom colors :
            margin:  bg de en-tête et footer
            action: boutons d'action 
            action2: actions secondaires
            access:  boutons pour les droits d'accès */
            colors: {
                'color-bg':        'var(--color-bg)',
                'color-header':    'var(--color-header)',
                'lightcolor-text': 'var(--lightcolor-text)',
                'darkcolor-text':  'var(--darkcolor-text)',
                'color-btn':       'var(--color-btn)',
                'hovercolor-btn':  'var(--hovercolor-btn )',
                'focuscolor-line': 'var(--focuscolor-line)',
                'hovercolor-line': 'var(--hovercolor-line)',
                page: colors.slate[50],
                header: colors.slate[500],
                headline: colors.orange[100],
                action: colors.slate[600],
                actionHover: colors.slate[500],
                action2: '#86a',
                access: '#0ff',
            },
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
    safelist: [
        'bg-color-header',
        'bg-header', 
        'bg-headline', 
        'bg-blue-100',
        'bg-red-100',
        'bg-green-100',
        'w-80', 'mr-4', 'py-1', 'px-2',
        'rounded', 'border', 'border-gray-300',
        'text-xs', 'file:font-medium',
        'bg-gray-50', 'text-gray-700',
        'hover:bg-gray-100', 'cursor-pointer',
        'file:mr-4', 'file:py-1', 'file:px-2',
        'file:rounded', 'file:border', 'file:border-gray-300',
        'file:text-xs', 'file:font-medium',
        'file:bg-gray-50', 'file:text-gray-700',
        'hover:file:bg-gray-100', 'file:cursor-pointer'

    ],
}
