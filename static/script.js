$(document).ready(function() {
    // Password visibility toggle
    $('#togglePassword').click(function() {
        const input = $('#passwordInput');
        const icon = $(this).find('i');
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            input.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // Password analysis
    $('#analyzeBtn').click(function() {
        const password = $('#passwordInput').val();
        if (!password) {
            alert("Please enter a password first!");
            return;
        }

        $('#resultCard').removeClass('hidden');
        $('#suggestions').addClass('hidden');
        $('#suggestionsList').empty();

        $.ajax({
            type: 'POST',
            url: '/analyze',
            contentType: 'application/json',
            data: JSON.stringify({ password: password }),
            success: function(data) {
                // Update strength meter
                const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-green-600'];
                const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
                
                $('#strengthMeter')
                    .removeClass()
                    .addClass(`h-2.5 rounded-full ${strengthColors[data.score]}`)
                    .css('width', `${(data.score + 1) * 20}%`);
                
                $('#strengthText').text(strengthLabels[data.score]);

                // Display results
                $('#crackTime').text(`Estimated crack time: ${data.crack_time}`);
                $('#feedback').text(data.feedback);
                
                // Show breach alert if needed
                if (data.breached) {
                    $('#breachAlert').removeClass('hidden');
                } else {
                    $('#breachAlert').addClass('hidden');
                }
                
                // Show suggestions if available
                if (data.suggestions && data.suggestions.length > 0) {
                    $('#suggestions').removeClass('hidden');
                    data.suggestions.forEach(s => {
                        $('#suggestionsList').append(`<li class="flex items-center">
                            <i class="fas fa-chevron-right text-xs text-blue-500 mr-2"></i>${s}
                        </li>`);
                    });
                }
            },
            error: function() {
                $('#feedback').text('Error analyzing password').addClass('text-red-500');
            }
        });
    });
});