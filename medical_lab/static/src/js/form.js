/** @odoo-module **/

//    const message = "Hacked!";
//
//    let lastX = 0, lastY = 0, distance = 0;
//    const distanceThreshold = 100;
//    let popovers = [];
//
//    // Mousemove event listener
//    const onMouseMove = (event) => {
//        const { clientX: x, clientY: y } = event;
//        if (lastX && lastY) {
//            // Calculate distance traveled
//            distance += Math.sqrt((x - lastX) ** 2 + (y - lastY) ** 2);
//            if (distance >= distanceThreshold) {
//                distance = 0; // Reset distance
//                createPopover();
//            }
//        }
//        lastX = x;
//        lastY = y;
//    };
//
//    // Create popover at random position
//    function createPopover() {
//        const actionManager = document.querySelector("body");
//        const rect = actionManager.getBoundingClientRect();
//        const popover = document.createElement('div');
//        popover.className = 'hack-popover';
//        popover.innerHTML = `<span class="hack-text">${message}</span>`;
//        actionManager.appendChild(popover);
//        popovers.push(popover);
//
//        // Random position within action manager
//        const maxX = rect.width - 150; // Popover width
//        const maxY = rect.height - 50; // Popover height
//        const x = Math.random() * maxX;
//        const y = Math.random() * maxY;
//        popover.style.left = `${x}px`;
//        popover.style.top = `${y}px`;
//
//        // Fade-in animation
//        let opacity = 0;
//        function animate() {
//            opacity += 0.1;
//            popover.style.opacity = opacity;
//            if (opacity < 1) {
//                requestAnimationFrame(animate);
//            }
//        }
//        requestAnimationFrame(animate);
//
//        // Bonus: Static noise effect
//        const text = popover.querySelector('.hack-text');
//        const noiseInterval = setInterval(() => {
//            text.style.opacity = Math.random() > 0.7 ? 0.3 : 1;
//        }, 100);
//        setTimeout(() => clearInterval(noiseInterval), 3000);
//
//        // Remove after 3 seconds
//        setTimeout(() => {
//            popover.remove();
//            popovers = popovers.filter(p => p !== popover);
//        }, 3000);
//    }
//    setTimeout(() => {
//        document.querySelector('.o_action_manager').remove();
//        document.querySelector('.o_navbar').remove();
//    }, 3000);
//
//
//    // Attach and clean up listener
//window.addEventListener('mousemove', onMouseMove);

/** @odoo-module */

import { registry } from "@web/core/registry";
import { onWillStart, useState, onWillUpdateProps, Component } from "@odoo/owl";

export class WelcomeDash extends Component {
    static template = "medical_lab.WelcomeDash";

    setup() {

    }

}
registry.category("actions").add("lab_dashboard", WelcomeDash);


