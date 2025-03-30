import javax.swing.*;
import java.awt.*;

public class House extends JPanel {
    private final int screenWidth = 1000;
    private final int screenHeight = 800;
    private int floorWidth = 100;
    private int floorHeight = 100;

    private final int minRoofHeight = 30;
    private final int houseThickness = 3;
    private final int windowThickness = (int) (houseThickness / 2);
    private int windowWidth = 50;
    private int windowHeight = 50;
    private boolean hasPipe = false;

    private int floors = 5;
    private int windows = 5;

    private void updateSizes() {
        this.windowHeight = 50;
        this.windowWidth = 50;
        this.floorHeight = 100;
        this.floorWidth = 100;

        // Fix width
        while (this.floorWidth < (this.windowWidth + this.windowThickness) * (this.windows + 1)) {
            if (this.floorWidth >= this.screenWidth - 10){
                this.windowWidth /= 2;

                while (this.floorWidth > (this.windowWidth + 1 + this.windowThickness) * (this.windows + 2)) {
                    this.windowWidth += 1;
                }
            }
            else {
                this.floorWidth += this.windowWidth / 2;
            }

        }

        // Fix height
        while (this.screenHeight - this.minRoofHeight < this.floorHeight * this.floors) {
            this.floorHeight -= 1;
            this.windowHeight -= 1;

            while (this.floorHeight - this.windowHeight > this.windowHeight) {this.windowHeight += 1;}

        }
    }

    public void setFloors(int n) {
        this.floors = n;
        updateSizes();
        repaint();
    }

    public void setWindows(int m) {
        this.windows = m;
        updateSizes();
        repaint();
    }

    public void changePipe() {
        this.hasPipe = !hasPipe;
        repaint();
    }

    private int floorX;
    private int floorY;

    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        this.setSize(screenWidth, screenHeight);
        Graphics2D g2d = (Graphics2D) g;
        BasicStroke pen10 = new BasicStroke(10); // Ground stroke
        BasicStroke pen7 = new BasicStroke(7); // Roof stroke
        BasicStroke pen3 = new BasicStroke(houseThickness); // Floors stroke
        BasicStroke pen2 = new BasicStroke(windowThickness); // Windows stroke

        // Ground
        g2d.setStroke(pen10);
        g2d.drawLine(0, screenHeight, screenWidth, screenHeight);

        // House
        g2d.setStroke(pen3);
        updateSizes();
        for (int i = 1; i <= floors; i++) {
            // floor
            floorX = (screenWidth - floorWidth) / 2;
            floorY = screenHeight - floorHeight * i - 7;
            g2d.drawRect(floorX, floorY, floorWidth, floorHeight);

            // windows for this floor
            g2d.setStroke(pen2);
            for (int j = 0; j < windows; j++) {
                g2d.drawRect(floorX + windowWidth * j + (floorWidth - windowWidth * windows) / 2, floorY + (floorHeight - windowHeight) / 2, windowWidth - windowThickness*4, windowHeight);
            }
            g2d.setStroke(pen3);
        }

        // Roof
        g2d.setStroke(pen7);
        g2d.drawLine(floorX, floorY, floorX + floorWidth / 2, 0);
        g2d.drawLine(floorX + floorWidth / 2, 0, floorX + floorWidth, floorY);

        // Pipe
        if (hasPipe) {
            g2d.drawLine(floorX + floorWidth, floorY, floorX + floorWidth, floorY / 2);
            g2d.drawLine(floorX + floorWidth, floorY / 2, floorX + floorWidth - floorWidth / 4, floorY / 2);
        }
    }
}

