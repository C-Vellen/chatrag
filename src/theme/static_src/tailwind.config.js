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
                page: colors.slate[100],
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
}
